#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-${CLAUDE_MODEL_OPTIMIZER_MODE:-${FABLE5_OPTIMIZER_MODE:-skill}}}"
REPO_URL="${CLAUDE_MODEL_OPTIMIZER_REPO_URL:-${FABLE5_OPTIMIZER_REPO_URL:-https://github.com/nyldn/claude-model-optimizer.git}}"
SKILL_NAME="claude-model-optimizer"
LEGACY_SKILL_NAME="fable5-optimizer"

usage() {
  cat <<'USAGE'
Usage:
  install.sh [skill|skill-project|claude-md|claude-md-print]

Modes:
  skill            Install to ~/.claude/skills/claude-model-optimizer. Default.
  skill-project    Install to ./.claude/skills/claude-model-optimizer for the current project.
  claude-md        Install a lightweight policy block to ./.claude/CLAUDE.md
                   plus the detailed project-local skill for on-demand use.
  claude-md-print  Print the generated block to stdout (used to regenerate
                   claude-md/CLAUDE.md in this repo).

Legacy aliases:
  user, global   Same as skill.
  project        Same as skill-project.
  always-on      Same as claude-md.
USAGE
}

print_next_step() {
  echo "Next: open a new Claude Code session and run /claude-model-optimizer."
}

case "$MODE" in
  -h|--help|help)
    usage
    exit 0
    ;;
esac

TMP_DIR=""
TMP_FILE=""
cleanup() {
  if [[ -n "$TMP_DIR" && -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
  if [[ -n "$TMP_FILE" && -e "$TMP_FILE" ]]; then
    rm -f "$TMP_FILE"
  fi
}
trap cleanup EXIT

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

backup_path() {
  local path="$1"
  local base="${path}.backup.$(date +%Y%m%d%H%M%S)"
  local candidate="$base"
  local counter=1

  while [[ -e "$candidate" ]]; do
    candidate="${base}.${counter}"
    counter=$((counter + 1))
  done

  printf '%s\n' "$candidate"
}

# Backups of a skill folder must not land inside a skills root: Claude Code
# discovers every directory that contains a SKILL.md, so a sibling backup would
# register as a second skill with the same name. Falls back to a temp directory
# when the skills root's parent is not writable, which happens with
# admin-managed skill locations.
skill_backup_dir() {
  local dest="$1"
  local skills_dir claude_dir candidate
  skills_dir="$(dirname "$dest")"
  claude_dir="$(dirname "$skills_dir")"
  candidate="$claude_dir/skill-backups"

  if mkdir -p "$candidate" 2>/dev/null; then
    printf '%s\n' "$candidate"
    return 0
  fi

  candidate="$(mktemp -d "${TMPDIR:-/tmp}/claude-model-optimizer-skill-backup.XXXXXX")"
  printf '%s\n' "$candidate"
}

# v2.0.0 wrote skill backups as siblings inside the skills root, where Claude
# Code still discovers them. Move any that a previous install left behind.
migrate_legacy_skill_backups() {
  local dest="$1"
  local legacy target backup_dir

  shopt -s nullglob
  local matches=("$dest".backup.*)
  shopt -u nullglob

  [[ "${#matches[@]}" -gt 0 ]] || return 0

  backup_dir="$(skill_backup_dir "$dest")"
  for legacy in "${matches[@]}"; do
    target="$(backup_path "$backup_dir/$(basename "$dest")")"
    mv "$legacy" "$target"
    echo "Moved a legacy in-root skill backup to $target"
  done
}

# The v3 rename changes Claude's discovery key. Preserve an old installation
# outside the skills root before writing the new one, so an upgrade cannot load
# both skills or discard local edits.
migrate_renamed_skill() {
  local dest="$1"
  local legacy_dest backup
  legacy_dest="$(dirname "$dest")/$LEGACY_SKILL_NAME"

  migrate_legacy_skill_backups "$legacy_dest"
  [[ -e "$legacy_dest" || -L "$legacy_dest" ]] || return 0

  backup="$(backup_path "$(skill_backup_dir "$dest")/$LEGACY_SKILL_NAME")"
  mv "$legacy_dest" "$backup"
  echo "Moved renamed $LEGACY_SKILL_NAME skill to $backup"
}

# The installer always writes CLAUDE.md with the invoking user's umask default.
# Preserving the destination's existing mode sounds safer but perpetuates the
# 0600 that v2.0.0 left behind, and reading the mode of a symlink reports the
# link's own bits rather than the target's.
default_file_mode() {
  printf '%o\n' "$(( 0666 & ~8#$(umask) ))"
}

script_dir=""
script_source="${BASH_SOURCE[0]:-}"
if [[ -n "$script_source" && -e "$script_source" ]]; then
  script_dir="$(cd "$(dirname "$script_source")" >/dev/null 2>&1 && pwd -P || true)"
fi

if [[ -n "$script_dir" && -d "$script_dir/skills/$SKILL_NAME" ]]; then
  SOURCE_DIR="$script_dir"
else
  require git
  TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/claude-model-optimizer.XXXXXX")"
  SOURCE_DIR="$TMP_DIR/repo"
  git clone --quiet --depth 1 "$REPO_URL" "$SOURCE_DIR"
fi

# Sets COPY_SKILL_CHANGED so callers can keep quiet about a no-op reinstall.
COPY_SKILL_CHANGED=0
copy_skill() {
  local src="$1"
  local dest="$2"

  COPY_SKILL_CHANGED=0
  migrate_renamed_skill "$dest"
  migrate_legacy_skill_backups "$dest"

  # A symlinked destination is never "already current": the caller asked for a
  # detached copy, and leaving the link means deleting the checkout it points at
  # would silently remove the installed skill.
  if [[ ! -L "$dest" && -d "$dest" ]] && diff -rq "$src" "$dest" >/dev/null 2>&1; then
    return 0
  fi
  COPY_SKILL_CHANGED=1

  if [[ -e "$dest" || -L "$dest" ]]; then
    local backup
    backup="$(backup_path "$(skill_backup_dir "$dest")/$(basename "$dest")")"
    mv "$dest" "$backup"
    echo "Backed up existing skill to $backup"
  fi

  mkdir -p "$(dirname "$dest")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$src"/ "$dest"/
  else
    mkdir -p "$dest"
    cp -R "$src"/. "$dest"/
  fi
}

# The always-on block stays deliberately small. Detailed guidance lives in
# the project-local skill that claude-md mode installs alongside it.
print_claude_md_block() {
  local policy_md="$SOURCE_DIR/claude-md/POLICY.md"

  if [[ ! -f "$policy_md" ]]; then
    echo "Missing always-on policy source: $policy_md" >&2
    exit 1
  fi

  printf '<!-- claude-model-optimizer:start -->\n'
  printf '<!-- Generated from claude-md/POLICY.md by install.sh. Do not hand-edit inside the markers. -->\n'
  cat "$policy_md"
  printf '<!-- claude-model-optimizer:end -->\n'
}

install_project_skill() {
  local target_dir="$1"
  local dest="$target_dir/.claude/skills/$SKILL_NAME"

  copy_skill "$SOURCE_DIR/skills/$SKILL_NAME" "$dest"
  if [[ "$COPY_SKILL_CHANGED" -eq 1 ]]; then
    echo "Installed project-local $SKILL_NAME skill to $dest"
  else
    echo "Project-local $SKILL_NAME skill already current at $dest"
  fi
}

claude_md_path() {
  local target_dir="${CLAUDE_MODEL_OPTIMIZER_TARGET:-${FABLE5_OPTIMIZER_TARGET:-$PWD}}"
  printf '%s\n' "${CLAUDE_MODEL_OPTIMIZER_CLAUDE_MD:-${FABLE5_OPTIMIZER_CLAUDE_MD:-$target_dir/.claude/CLAUDE.md}}"
}

# Echo the file with the managed block and any trailing blank lines removed, so
# rerunning the installer reproduces the same bytes instead of growing a blank
# line. Markers must match a whole line: the marker text also appears in prose
# documenting this mechanism, and treating that as a block opener would discard
# everything after it. Exits 3 on a block that is opened and never closed,
# rather than silently truncating the file.
strip_managed_block() {
  awk \
    -v new_start='^[[:space:]]*<!-- claude-model-optimizer:start -->[[:space:]]*$' \
    -v new_end='^[[:space:]]*<!-- claude-model-optimizer:end -->[[:space:]]*$' \
    -v old_start='^[[:space:]]*<!-- fable5-optimizer:start -->[[:space:]]*$' \
    -v old_end='^[[:space:]]*<!-- fable5-optimizer:end -->[[:space:]]*$' '
    $0 ~ new_start && !skip { skip = "new"; count = 0; next }
    $0 ~ old_start && !skip { skip = "old"; count = 0; next }
    $0 ~ new_end && skip == "new" { skip = ""; next }
    $0 ~ old_end && skip == "old" { skip = ""; next }
    skip { next }
    /^[[:space:]]*$/ { pending[count++] = $0; next }
    {
      for (i = 0; i < count; i++) print pending[i]
      count = 0
      print
    }
    END { if (skip) exit 3 }
  ' "$1"
}

unterminated_block_error() {
  echo "Refusing to install: $1 opens a model-optimizer block that is never closed." >&2
  echo "Repair or remove the managed block by hand, then rerun." >&2
  exit 1
}

# Run before any other install step so a rejected destination does not leave a
# half-finished install behind. Only a regular file, or a symlink to one, can
# hold the policy block; without this check a directory at the destination
# silently absorbs the staging file and the installer reports success with
# nothing installed.
validate_claude_md_dest() {
  local dest
  dest="$(claude_md_path)"

  if [[ -e "$dest" && ! -f "$dest" ]]; then
    echo "Refusing to install: $dest exists and is not a regular file." >&2
    exit 1
  fi

  if [[ -f "$dest" ]] && ! strip_managed_block "$dest" >/dev/null; then
    unterminated_block_error "$dest"
  fi
}

install_claude_md() {
  local dest dest_dir

  dest="$(claude_md_path)"
  dest_dir="$(dirname "$dest")"
  mkdir -p "$dest_dir"
  validate_claude_md_dest

  # Clear any staging file a previously killed run left behind, so an
  # uncatchable termination cannot leave a stray copy of the user's
  # instructions in the project indefinitely.
  rm -f "$dest_dir"/.claude-model-optimizer-claude.* "$dest_dir"/.fable5-optimizer-claude.* 2>/dev/null || true

  # Stage in the destination directory so the final move is atomic and never
  # crosses a filesystem boundary.
  TMP_FILE="$(mktemp "$dest_dir/.claude-model-optimizer-claude.XXXXXX")"

  if [[ -f "$dest" ]] && ! strip_managed_block "$dest" > "$TMP_FILE"; then
    unterminated_block_error "$dest"
  fi

  if [[ -s "$TMP_FILE" ]]; then
    printf '\n' >> "$TMP_FILE"
  fi
  print_claude_md_block >> "$TMP_FILE"

  if [[ -f "$dest" ]] && cmp -s "$TMP_FILE" "$dest"; then
    rm -f "$TMP_FILE"
    TMP_FILE=""
    # The content can already match while the mode is still wrong, which is
    # exactly the state v2.0.0 left behind.
    if [[ ! -L "$dest" ]]; then
      chmod "$(default_file_mode)" "$dest"
    fi
    echo "Always-on $SKILL_NAME policy already current at $dest"
    return 0
  fi

  if [[ -f "$dest" ]]; then
    local backup
    backup="$(backup_path "$dest")"
    cp "$dest" "$backup"
    echo "Backed up existing CLAUDE.md to $backup"
  fi

  if [[ -L "$dest" ]]; then
    # Write through the link so a dotfiles-managed CLAUDE.md keeps its
    # indirection and the real target keeps its own mode.
    cat "$TMP_FILE" > "$dest"
    rm -f "$TMP_FILE"
  else
    # mktemp creates 0600; use the umask default so an installed CLAUDE.md is
    # readable like any other file this user writes.
    chmod "$(default_file_mode)" "$TMP_FILE"
    mv "$TMP_FILE" "$dest"
  fi
  TMP_FILE=""
  echo "Installed always-on $SKILL_NAME policy to $dest"
}

case "$MODE" in
  skill|user|global)
    DEST="${CLAUDE_MODEL_OPTIMIZER_SKILLS_DIR:-${FABLE5_OPTIMIZER_SKILLS_DIR:-$HOME/.claude/skills}}/$SKILL_NAME"
    copy_skill "$SOURCE_DIR/skills/$SKILL_NAME" "$DEST"
    if [[ "$COPY_SKILL_CHANGED" -eq 1 ]]; then
      echo "Installed $SKILL_NAME to $DEST"
    else
      echo "$SKILL_NAME already current at $DEST"
    fi
    print_next_step
    ;;

  skill-project|project)
    TARGET_DIR="${CLAUDE_MODEL_OPTIMIZER_TARGET:-${FABLE5_OPTIMIZER_TARGET:-$PWD}}"
    install_project_skill "$TARGET_DIR"
    print_next_step
    ;;

  claude-md|always-on)
    TARGET_DIR="${CLAUDE_MODEL_OPTIMIZER_TARGET:-${FABLE5_OPTIMIZER_TARGET:-$PWD}}"
    # Reject a bad CLAUDE.md destination before touching anything else, so a
    # refusal never leaves a half-finished install behind.
    validate_claude_md_dest
    install_project_skill "$TARGET_DIR"
    install_claude_md
    print_next_step
    ;;

  claude-md-print)
    print_claude_md_block
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac

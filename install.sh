#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="model-optimizer-lite"
ACTION=install
MODE="${1:-${MODEL_OPTIMIZER_LITE_MODE:-choose}}"
PROJECT=0
case "$MODE" in
  install|update|status|uninstall)
    ACTION="$MODE"
    MODE="${2:-choose}"
    [[ "$ACTION" != status || "$MODE" != choose ]] || MODE=both
    [[ "${3:-}" != --project ]] || PROJECT=1
    [[ $# -le 3 && ( $# -lt 3 || "${3:-}" == --project ) ]] || MODE=invalid
    ;;
  *)
    [[ "${2:-}" != --project ]] || PROJECT=1
    [[ $# -le 2 && ( $# -lt 2 || "${2:-}" == --project ) ]] || MODE=invalid
    ;;
esac

usage() {
  cat <<'USAGE'
Usage: install.sh [action] <app> [--project]

Install for the app you use:
  install.sh claude             Claude Code, including local desktop Code sessions
  install.sh codex              Codex local coding sessions
  install.sh both               Both apps
  install.sh                   Choose interactively in a terminal

Manage a direct skill installation:
  install.sh status [claude|codex|both] [--project]
  install.sh update <claude|codex|both> [--project]
  install.sh uninstall <claude|codex|both> [--project]

Add --project to install only in the current project.
Update downloads a fresh source; it never changes your checkout.
Uninstall archives the skill outside discovery so local edits can be recovered.
Status checks local files, not whether an app has loaded them.

Claude chat/Cowork: upload the skill ZIP through Customize > Skills instead.
Native plugin installs: manage updates/removal in the app's plugin manager.

Advanced modes:
  skill, skill-project          Direct Claude user/project skill
  codex-project                Direct Codex project skill
  claude-md                    Project skill plus a short always-on policy
  claude-md-print              Print that policy for maintainers
USAGE
}

print_next_step() {
  echo "Next: open a new Claude Code session and run /model-optimizer-lite."
}

case "$MODE" in
  -h|--help|help)
    usage
    exit 0
    ;;
  choose)
    if [[ "$ACTION" != install ]] || ! ( : < /dev/tty ) 2>/dev/null; then
      usage >&2
      echo "Choose an app explicitly: claude, codex, or both." >&2
      exit 2
    fi
    printf 'Install for 1) Claude Code  2) Codex  3) Both: ' > /dev/tty
    read -r choice < /dev/tty
    case "$choice" in
      1|claude) MODE=claude ;;
      2|codex) MODE=codex ;;
      3|both) MODE=both ;;
      *) echo "No installation made. Choose claude, codex, or both." >&2; exit 2 ;;
    esac
    ;;
  claude|codex|both|skill|skill-project|codex-project|claude-md|claude-md-print) ;;
  *) usage >&2; exit 2 ;;
esac
if [[ "$ACTION" != install ]]; then
  case "$MODE" in claude|codex|both) ;; *) usage >&2; exit 2 ;; esac
fi
if [[ "$PROJECT" == 1 ]]; then
  case "$MODE" in claude|codex|both) ;; *) usage >&2; exit 2 ;; esac
fi
case "$MODE" in
  skill) MODE=claude ;;
  skill-project) MODE=claude; PROJECT=1 ;;
  codex-project) MODE=codex; PROJECT=1 ;;
esac

TMP_DIR=""
TMP_FILE=""
TMP_SKILL=""
cleanup() {
  if [[ -n "$TMP_DIR" && -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
  if [[ -n "$TMP_FILE" && -e "$TMP_FILE" ]]; then
    rm -f "$TMP_FILE"
  fi
  if [[ -n "$TMP_SKILL" && -d "$TMP_SKILL" ]]; then
    rm -rf "$TMP_SKILL"
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

  candidate="$(mktemp -d "${TMPDIR:-/tmp}/model-optimizer-lite-skill-backup.XXXXXX")"
  printf '%s\n' "$candidate"
}

# Use the invoking user's umask for regular CLAUDE.md files.
default_file_mode() {
  printf '%o\n' "$(( 0666 & ~8#$(umask) ))"
}

script_dir=""
script_source="${BASH_SOURCE[0]:-}"
if [[ -n "$script_source" && -e "$script_source" ]]; then
  script_dir="$(cd "$(dirname "$script_source")" >/dev/null 2>&1 && pwd -P || true)"
fi

resolve_source() {
  if [[ "$ACTION" != update && -n "$script_dir" && -d "$script_dir/skills/$SKILL_NAME" ]]; then
    SOURCE_DIR="$script_dir"
    return
  fi
  TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/model-optimizer-lite.XXXXXX")"
  SOURCE_DIR="$TMP_DIR/repo"
  if [[ -n "${MODEL_OPTIMIZER_LITE_REPO_URL:-}" ]]; then
    require git
    git clone --quiet --depth 1 "${MODEL_OPTIMIZER_LITE_REPO_URL}" "$SOURCE_DIR"
  else
    require curl
    require tar
    local ref="${MODEL_OPTIMIZER_LITE_REF:-}" url
    url="https://github.com/nyldn/model-optimizer-lite/releases/latest/download/model-optimizer-lite-source.tar.gz"
    if [[ -n "$ref" ]]; then
      [[ "$ref" =~ ^[a-zA-Z0-9._-]+$ ]] || { echo "Invalid source ref." >&2; exit 2; }
      url="https://codeload.github.com/nyldn/model-optimizer-lite/tar.gz/$ref"
    fi
    echo "Downloading Model Optimizer Lite (${ref:-latest release})..."
    curl --fail --silent --show-error --location --connect-timeout 15 --max-time 120 \
      "$url" -o "$TMP_DIR/source.tar.gz"
    mkdir -p "$SOURCE_DIR"
    tar -xzf "$TMP_DIR/source.tar.gz" --strip-components=1 -C "$SOURCE_DIR"
  fi
  [[ -f "$SOURCE_DIR/skills/$SKILL_NAME/SKILL.md" ]] || { echo "Download is missing the skill." >&2; exit 1; }
}

# Sets COPY_SKILL_CHANGED so callers can keep quiet about a no-op reinstall.
COPY_SKILL_CHANGED=0
copy_skill() {
  local src="$1"
  local dest="$2"

  COPY_SKILL_CHANGED=0
  # A symlinked destination is never "already current": the caller asked for a
  # detached copy, and leaving the link means deleting the checkout it points at
  # would silently remove the installed skill.
  if [[ ! -L "$dest" && -d "$dest" ]] && diff -rq "$src" "$dest" >/dev/null 2>&1; then
    return 0
  fi
  COPY_SKILL_CHANGED=1

  # Copy first so a failed transfer leaves the current installation intact.
  mkdir -p "$(dirname "$dest")" || return 1
  TMP_SKILL="$(mktemp -d "$(dirname "$(dirname "$dest")")/.model-optimizer-lite-stage.XXXXXX")" || return 1
  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$src"/ "$TMP_SKILL"/ || return 1
  else
    cp -R "$src"/. "$TMP_SKILL"/ || return 1
  fi
  diff -rq "$src" "$TMP_SKILL" >/dev/null || return 1
  local backup=""
  if [[ -e "$dest" || -L "$dest" ]]; then
    backup="$(backup_path "$(skill_backup_dir "$dest")/$(basename "$dest")")"
    mv "$dest" "$backup" || return 1
    echo "Backed up existing skill to $backup"
  fi
  if ! mv "$TMP_SKILL" "$dest"; then
    [[ -z "$backup" ]] || mv "$backup" "$dest"
    return 1
  fi
  TMP_SKILL=""
}

# The always-on block stays deliberately small. Detailed guidance lives in
# the project-local skill that claude-md mode installs alongside it.
print_claude_md_block() {
  local policy_md="$SOURCE_DIR/claude-md/POLICY.md"

  if [[ ! -f "$policy_md" ]]; then
    echo "Missing always-on policy source: $policy_md" >&2
    exit 1
  fi

  printf '<!-- model-optimizer-lite:start -->\n'
  printf '<!-- Generated from claude-md/POLICY.md by install.sh. Do not hand-edit inside the markers. -->\n'
  cat "$policy_md"
  printf '<!-- model-optimizer-lite:end -->\n'
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
  local target_dir="${MODEL_OPTIMIZER_LITE_TARGET:-$PWD}"
  printf '%s\n' "${MODEL_OPTIMIZER_LITE_CLAUDE_MD:-$target_dir/.claude/CLAUDE.md}"
}

# Echo the file with the managed block and any trailing blank lines removed, so
# rerunning the installer reproduces the same bytes instead of growing a blank
# line. Markers must match a whole line: the marker text also appears in prose
# documenting this mechanism, and treating that as a block opener would discard
# everything after it. Exits 3 on a block that is opened and never closed,
# rather than silently truncating the file.
strip_managed_block() {
  awk \
    -v start='^[[:space:]]*<!-- model-optimizer-lite:start -->[[:space:]]*$' \
    -v end='^[[:space:]]*<!-- model-optimizer-lite:end -->[[:space:]]*$' '
    $0 ~ start && !skip { skip = 1; count = 0; next }
    $0 ~ end && skip { skip = 0; next }
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
  rm -f "$dest_dir"/.model-optimizer-lite-claude.* 2>/dev/null || true

  # Stage in the destination directory so the final move is atomic and never
  # crosses a filesystem boundary.
  TMP_FILE="$(mktemp "$dest_dir/.model-optimizer-lite-claude.XXXXXX")"

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
    # Apply the mode policy even when the content is already current.
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

skill_dest() {
  local host="$1" root
  if [[ "$host" == claude ]]; then
    root="${MODEL_OPTIMIZER_LITE_CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
    [[ "$PROJECT" == 0 ]] || root="${MODEL_OPTIMIZER_LITE_TARGET:-$PWD}/.claude/skills"
  else
    root="${MODEL_OPTIMIZER_LITE_CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
    [[ "$PROJECT" == 0 ]] || root="${MODEL_OPTIMIZER_LITE_TARGET:-$PWD}/.agents/skills"
  fi
  printf '%s/%s\n' "$root" "$SKILL_NAME"
}

verify_skill() {
  local dest="$1"
  [[ -f "$dest/SKILL.md" && -f "$dest/VERSION" && -f "$dest/FILES.sha256" ]] || return 1
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "$dest" && sha256sum -c FILES.sha256 >/dev/null 2>&1)
  elif command -v shasum >/dev/null 2>&1; then
    (cd "$dest" && shasum -a 256 -c FILES.sha256 >/dev/null 2>&1)
  else
    echo "Install verification needs sha256sum or shasum." >&2
    return 1
  fi
}

remove_policy() {
  local dest
  dest="$(claude_md_path)"
  [[ -f "$dest" ]] || return 0
  grep -q '^[[:space:]]*<!-- model-optimizer-lite:start -->[[:space:]]*$' "$dest" || return 0
  validate_claude_md_dest
  TMP_FILE="$(mktemp "$(dirname "$dest")/.model-optimizer-lite-remove.XXXXXX")" || return 1
  strip_managed_block "$dest" > "$TMP_FILE" || return 1
  cp "$dest" "$(backup_path "$dest")" || return 1
  if [[ -L "$dest" ]]; then
    cat "$TMP_FILE" > "$dest" || return 1
    rm -f "$TMP_FILE"
  else
    chmod "$(default_file_mode)" "$TMP_FILE" || return 1
    mv "$TMP_FILE" "$dest" || return 1
  fi
  TMP_FILE=""
  echo "Removed the Model Optimizer Lite policy from $dest; other instructions retained."
}

manage_skill() {
  local host="$1" dest backup
  dest="$(skill_dest "$host")"
  case "$ACTION" in
    status)
      if [[ ! -e "$dest" && ! -L "$dest" ]]; then
        echo "$host: not installed at $dest"
        return 1
      elif verify_skill "$dest"; then
        echo "$host: version $(cat "$dest/VERSION"), package files verified at $dest"
      else
        echo "$host: incomplete, modified, or unversioned installation at $dest"
        return 1
      fi
      ;;
    uninstall)
      if [[ "$host" == claude && "$PROJECT" == 1 ]]; then
        validate_claude_md_dest
        remove_policy || return 1
      fi
      if [[ -e "$dest" || -L "$dest" ]]; then
        backup="$(backup_path "$(skill_backup_dir "$dest")/$(basename "$dest")")"
        mv "$dest" "$backup" || return 1
        echo "$host: uninstalled. Recoverable copy: $backup"
      else
        echo "$host: not installed. Nothing changed."
      fi
      ;;
    install|update)
      if [[ "$ACTION" == update && ! -e "$dest" && ! -L "$dest" ]]; then
        echo "$host: not installed; skipped. Use 'install.sh $host' to install."
        return 0
      fi
      verify_skill "$SOURCE_DIR/skills/$SKILL_NAME" || { echo "Source package verification failed; nothing installed." >&2; return 1; }
      if ! copy_skill "$SOURCE_DIR/skills/$SKILL_NAME" "$dest"; then
        [[ -z "$TMP_SKILL" ]] || rm -rf "$TMP_SKILL"
        TMP_SKILL=""
        echo "$host: installation failed; check directory permissions and the error above." >&2
        return 1
      fi
      verify_skill "$dest" || { echo "Installed file verification failed at $dest" >&2; return 1; }
      echo "$host: version $(cat "$dest/VERSION") installed and package files verified."
      if [[ "$host" == claude ]]; then print_next_step
      else echo 'Next: open a new Codex session and invoke $model-optimizer-lite.'; fi
      ;;
  esac
}

case "$MODE" in
  claude|codex|both)
    if [[ "$ACTION" == install || "$ACTION" == update ]]; then resolve_source; fi
    UPDATE_POLICY=0
    if [[ "$ACTION" == update && "$PROJECT" == 1 && "$MODE" != codex ]]; then
      policy_dest="$(claude_md_path)"
      if [[ -f "$policy_dest" ]] && grep -q '^[[:space:]]*<!-- model-optimizer-lite:start -->[[:space:]]*$' "$policy_dest"; then
        validate_claude_md_dest
        UPDATE_POLICY=1
      fi
    fi
    result=0
    if [[ "$MODE" == claude || "$MODE" == both ]]; then
      manage_skill claude || result=1
    fi
    if [[ "$MODE" == codex || "$MODE" == both ]]; then
      manage_skill codex || result=1
    fi
    if [[ "$result" == 0 && "$UPDATE_POLICY" == 1 ]]; then install_claude_md; fi
    [[ "$ACTION" != status ]] || echo "This checks direct skill files only. Start a new session and invoke the skill to confirm app discovery."
    exit "$result"
    ;;
esac

resolve_source
case "$MODE" in
  claude-md)
    TARGET_DIR="${MODEL_OPTIMIZER_LITE_TARGET:-$PWD}"
    # Reject a bad CLAUDE.md destination before touching anything else, so a
    # refusal never leaves a half-finished install behind.
    validate_claude_md_dest
    verify_skill "$SOURCE_DIR/skills/$SKILL_NAME" || { echo "Source package verification failed." >&2; exit 1; }
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

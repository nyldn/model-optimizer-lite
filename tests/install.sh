#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-model-optimizer-test.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

# install.sh reads all of these from the environment. An inherited value would
# send an install outside the sandbox below, at a real ~/.claude in the worst
# case, so clear them before the first run.
unset AI_MODEL_OPTIMIZER_MODE
unset AI_MODEL_OPTIMIZER_TARGET
unset AI_MODEL_OPTIMIZER_CLAUDE_SKILLS_DIR
unset AI_MODEL_OPTIMIZER_CLAUDE_MD
unset AI_MODEL_OPTIMIZER_REPO_URL
unset AI_MODEL_OPTIMIZER_CODEX_SKILLS_DIR

HOME_DIR="$TMP_DIR/home"
PROJECT_DIR="$TMP_DIR/project"
mkdir -p "$HOME_DIR" "$PROJECT_DIR"

# Public installers should explain themselves without attempting an install.
HELP_OUTPUT="$("$ROOT/install.sh" --help)"
grep -q "Usage:" <<< "$HELP_OUTPUT"
grep -q "skill-project" <<< "$HELP_OUTPUT"
grep -q "claude-md" <<< "$HELP_OUTPUT"
PIPE_HELP_OUTPUT="$(AI_MODEL_OPTIMIZER_REPO_URL="invalid://must-not-clone" bash -s -- --help < "$ROOT/install.sh")"
grep -q "Usage:" <<< "$PIPE_HELP_OUTPUT"

# GNU stat first; BSD stat rejects -c cleanly, while GNU -f means
# --file-system and would print filesystem details for the path before failing.
file_mode() {
  local mode
  if mode="$(stat -c '%a' "$1" 2>/dev/null)"; then
    printf '%s\n' "$mode"
    return 0
  fi
  stat -f '%Lp' "$1" 2>/dev/null
}

umask_default_mode() {
  printf '%o\n' "$(( 0666 & ~8#$(umask) ))"
}

backup_inventory() {
  find "$1" -name '*.backup.*' | sort
}

USER_INSTALL_OUTPUT="$(HOME="$HOME_DIR" "$ROOT/install.sh" skill)"
test -f "$HOME_DIR/.claude/skills/ai-model-optimizer/SKILL.md"
grep -q "run /ai-model-optimizer" <<< "$USER_INSTALL_OUTPUT"

# Exercise the same stdin execution path used by the README curl command. Build
# a temporary Git repository from the working tree so a pre-commit run covers
# renamed files as well as installer edits without touching the network.
PIPE_REPO="$TMP_DIR/pipe-repo"
mkdir -p "$PIPE_REPO"
(cd "$ROOT" && tar --exclude=.git -cf - .) | (cd "$PIPE_REPO" && tar -xf -)
git -C "$PIPE_REPO" init -q
git -C "$PIPE_REPO" config user.email "test@example.invalid"
git -C "$PIPE_REPO" config user.name "Installer Test"
git -C "$PIPE_REPO" add .
git -C "$PIPE_REPO" commit -qm "fixture"

PIPE_HOME="$TMP_DIR/pipe-home"
mkdir -p "$PIPE_HOME"
PIPE_INSTALL_OUTPUT="$(HOME="$PIPE_HOME" AI_MODEL_OPTIMIZER_REPO_URL="file://$PIPE_REPO" bash < "$ROOT/install.sh")"
test -f "$PIPE_HOME/.claude/skills/ai-model-optimizer/SKILL.md"
grep -q "run /ai-model-optimizer" <<< "$PIPE_INSTALL_OUTPUT"

AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" skill-project
test -f "$PROJECT_DIR/.claude/skills/ai-model-optimizer/SKILL.md"

mkdir -p "$PROJECT_DIR/.claude"
printf '# Project Instructions\n\nKeep this project-specific note.\n\t\nTrailing-whitespace line above must survive.\n' > "$PROJECT_DIR/.claude/CLAUDE.md"

AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" claude-md
test -f "$PROJECT_DIR/.claude/CLAUDE.md"
test -f "$PROJECT_DIR/.claude/skills/ai-model-optimizer/SKILL.md"
test -f "$PROJECT_DIR/.claude/skills/ai-model-optimizer/references/codex-workflows.md"
grep -q "Keep this project-specific note." "$PROJECT_DIR/.claude/CLAUDE.md"
grep -q "# Model Routing" "$PROJECT_DIR/.claude/CLAUDE.md"
grep -q "Claude Opus 5" "$PROJECT_DIR/.claude/CLAUDE.md"
grep -q "GPT-5.6 Sol" "$PROJECT_DIR/.claude/CLAUDE.md"
grep -q "/ai-model-optimizer" "$PROJECT_DIR/.claude/CLAUDE.md"
grep -q "ai-model-optimizer:start" "$PROJECT_DIR/.claude/CLAUDE.md"
# Interior whitespace-only lines are user content and must be preserved byte
# for byte; only trailing blank lines are trimmed.
grep -q "^	$" "$PROJECT_DIR/.claude/CLAUDE.md"

cp "$PROJECT_DIR/.claude/CLAUDE.md" "$TMP_DIR/first-run.md"

# Rerunning must be a byte-for-byte no-op: no stacked blocks, no growing blank
# lines, no fresh backup of content that did not change.
AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" claude-md
AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" claude-md
test "$(grep -c "ai-model-optimizer:start" "$PROJECT_DIR/.claude/CLAUDE.md")" -eq 1
diff -u "$TMP_DIR/first-run.md" "$PROJECT_DIR/.claude/CLAUDE.md"
test "$(find "$PROJECT_DIR/.claude" -name 'CLAUDE.md.backup.*' | wc -l | tr -d ' ')" -eq 1

# The installer applies the umask default rather than whatever mode the file
# happened to carry. 0604 is unreachable from any umask, so an implementation
# that preserved the existing mode instead would fail here.
chmod 604 "$PROJECT_DIR/.claude/CLAUDE.md"
AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" claude-md
test "$(file_mode "$PROJECT_DIR/.claude/CLAUDE.md")" = "$(umask_default_mode)"

# A run that does change the content backs up the previous version, not just
# the very first install.
printf '\n## Hand edit\n' >> "$PROJECT_DIR/.claude/CLAUDE.md"
AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" claude-md
test "$(find "$PROJECT_DIR/.claude" -name 'CLAUDE.md.backup.*' | wc -l | tr -d ' ')" -eq 2
grep -q "## Hand edit" "$PROJECT_DIR/.claude/CLAUDE.md"

# Skill backups must live outside the skills root; Claude Code discovers every
# directory below it that contains a SKILL.md, so a backup left there would
# register as a second skill claiming the same name.
printf '\nlocal edit\n' >> "$PROJECT_DIR/.claude/skills/ai-model-optimizer/SKILL.md"
AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" skill-project
test "$(find "$PROJECT_DIR/.claude/skills" -name 'SKILL.md' | wc -l | tr -d ' ')" -eq 1
test "$(find "$PROJECT_DIR/.claude/skill-backups" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')" -eq 1
grep -q "local edit" "$PROJECT_DIR"/.claude/skill-backups/ai-model-optimizer.backup.*/SKILL.md
! grep -q "local edit" "$PROJECT_DIR/.claude/skills/ai-model-optimizer/SKILL.md"

# An unchanged skill reinstall creates no backup artifact anywhere in the tree.
backup_inventory "$PROJECT_DIR" > "$TMP_DIR/backups-before.txt"
AI_MODEL_OPTIMIZER_TARGET="$PROJECT_DIR" "$ROOT/install.sh" skill-project
backup_inventory "$PROJECT_DIR" > "$TMP_DIR/backups-after.txt"
diff -u "$TMP_DIR/backups-before.txt" "$TMP_DIR/backups-after.txt"

# A symlinked skill destination is replaced with a real copy. Leaving the link
# means deleting the checkout it points at silently removes the installed skill.
LINK_SKILL_DIR="$TMP_DIR/link-skill"
mkdir -p "$LINK_SKILL_DIR/.claude/skills" "$LINK_SKILL_DIR/checkout"
cp -R "$ROOT/skills/ai-model-optimizer/." "$LINK_SKILL_DIR/checkout/"
ln -s ../../checkout "$LINK_SKILL_DIR/.claude/skills/ai-model-optimizer"
AI_MODEL_OPTIMIZER_TARGET="$LINK_SKILL_DIR" "$ROOT/install.sh" skill-project
test ! -L "$LINK_SKILL_DIR/.claude/skills/ai-model-optimizer"
test -f "$LINK_SKILL_DIR/.claude/skills/ai-model-optimizer/SKILL.md"

# A CLAUDE.md created from scratch gets the umask default, not mktemp's 0600.
FRESH_DIR="$TMP_DIR/fresh"
mkdir -p "$FRESH_DIR"
(
  umask 027
  AI_MODEL_OPTIMIZER_TARGET="$FRESH_DIR" "$ROOT/install.sh" claude-md
  test "$(file_mode "$FRESH_DIR/.claude/CLAUDE.md")" = "$(umask_default_mode)"
)

# The marker text appears in prose that documents this mechanism. Matching it
# mid-line would treat the sentence as a block opener and discard the rest of
# the file.
PROSE_DIR="$TMP_DIR/prose"
mkdir -p "$PROSE_DIR/.claude"
printf '# House rules\n\nMarkers look like <!-- ai-model-optimizer:start --> in our docs.\n\n## Secrets\n\nNever commit credentials.\n' > "$PROSE_DIR/.claude/CLAUDE.md"
AI_MODEL_OPTIMIZER_TARGET="$PROSE_DIR" "$ROOT/install.sh" claude-md
grep -q "Never commit credentials." "$PROSE_DIR/.claude/CLAUDE.md"
grep -q "Markers look like" "$PROSE_DIR/.claude/CLAUDE.md"

# A block that is opened and never closed is a refusal, not a silent
# truncation, and nothing else is installed.
BROKEN_DIR="$TMP_DIR/broken"
mkdir -p "$BROKEN_DIR/.claude"
printf '# A\n<!-- ai-model-optimizer:start -->\nstale block\n\n## Keep me\n' > "$BROKEN_DIR/.claude/CLAUDE.md"
if AI_MODEL_OPTIMIZER_TARGET="$BROKEN_DIR" "$ROOT/install.sh" claude-md >/dev/null 2>&1; then
  echo "expected a refusal for an unterminated managed block" >&2
  exit 1
fi
grep -q "## Keep me" "$BROKEN_DIR/.claude/CLAUDE.md"
test ! -d "$BROKEN_DIR/.claude/skills"

# A destination that is not a regular file is a refusal, not a success message
# with a stray dotfile hidden inside the directory.
DIR_DEST="$TMP_DIR/dir-dest"
mkdir -p "$DIR_DEST/.claude/CLAUDE.md"
if AI_MODEL_OPTIMIZER_TARGET="$DIR_DEST" "$ROOT/install.sh" claude-md >/dev/null 2>&1; then
  echo "expected a refusal for a directory at the CLAUDE.md destination" >&2
  exit 1
fi
test ! -d "$DIR_DEST/.claude/skills"
test -z "$(find "$DIR_DEST/.claude/CLAUDE.md" -mindepth 1)"

# A symlinked CLAUDE.md is written through, so a dotfiles-managed file keeps
# its indirection and the real target keeps its own mode.
LINK_DIR="$TMP_DIR/link"
mkdir -p "$LINK_DIR/proj/.claude" "$LINK_DIR/shared"
printf '# shared rules\n' > "$LINK_DIR/shared/CLAUDE.md"
chmod 644 "$LINK_DIR/shared/CLAUDE.md"
ln -s ../../shared/CLAUDE.md "$LINK_DIR/proj/.claude/CLAUDE.md"
AI_MODEL_OPTIMIZER_TARGET="$LINK_DIR/proj" "$ROOT/install.sh" claude-md
test -L "$LINK_DIR/proj/.claude/CLAUDE.md"
grep -q "# Model Routing" "$LINK_DIR/shared/CLAUDE.md"
grep -q "# shared rules" "$LINK_DIR/shared/CLAUDE.md"
test "$(file_mode "$LINK_DIR/shared/CLAUDE.md")" = "644"

echo "OK: install modes validated"

# Installation

The default install adds Claude Model Optimizer to your Claude Code user skills. It works across projects and does not change any project files.

## Requirements

- Claude Code with skills support
- Git
- Bash
- curl for the one-line installer
- macOS, Linux, or Windows through WSL

Codex is optional. Install and authenticate the Codex CLI only if you want Claude to delegate work to Codex.

Check the tools you plan to use:

```bash
claude --version
git --version
curl --version
codex --version
```

## Install for your user account

Copy and run:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh | bash
```

The installer copies the skill to:

```text
~/.claude/skills/claude-model-optimizer/
```

Confirm it is present:

```bash
test -f "$HOME/.claude/skills/claude-model-optimizer/SKILL.md" && echo "claude-model-optimizer is installed"
```

Open a new Claude Code session, then run:

```text
/claude-model-optimizer should Opus own this work, or does it need Fable?
```

## Inspect before installing

If you do not want to pipe a remote script into Bash, clone the repository and inspect the installer first:

```bash
git clone https://github.com/nyldn/claude-model-optimizer.git
cd claude-model-optimizer
./install.sh --help
./install.sh skill
```

## Install for one project

Run this from the project's root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh | bash -s -- skill-project
```

This writes the skill to:

```text
./.claude/skills/claude-model-optimizer/
```

Confirm it is present:

```bash
test -f ".claude/skills/claude-model-optimizer/SKILL.md" && echo "project skill is installed"
```

## Install the always-on router

Use this mode when you want a short routing policy loaded in every Claude Code session for one project. Run it from that project's root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh | bash -s -- claude-md
```

This mode makes two changes:

1. It installs the detailed skill at `.claude/skills/claude-model-optimizer/`.
2. It adds a managed block to `.claude/CLAUDE.md`.

The block starts and ends with these markers:

```html
<!-- claude-model-optimizer:start -->
<!-- claude-model-optimizer:end -->
```

The installer preserves everything outside that block. If the file changes, it writes a timestamped backup beside the original before replacing it. An incomplete managed block causes the installer to stop without changing the file.

## Update

Rerun the same command you used to install. The installer compares the installed files with the current repository and skips files that have not changed.

For the default user install:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh | bash
```

When an installed skill has local changes, the installer moves the old folder to `~/.claude/skill-backups/` for a user install or `.claude/skill-backups/` for a project install.

### Upgrade from `fable5-optimizer`

Version 3 renames the skill and its invocation to `claude-model-optimizer`. Rerun the installer once. It will:

1. Move the old `fable5-optimizer` skill folder into the existing `skill-backups` directory so local edits are preserved outside Claude's discovery path.
2. Install the skill under `claude-model-optimizer`.
3. Replace an old `fable5-optimizer` managed block with one `claude-model-optimizer` block while preserving the rest of `CLAUDE.md`.

Open a new Claude Code session after the upgrade and invoke `/claude-model-optimizer`. Environment settings should use the `CLAUDE_MODEL_OPTIMIZER_` prefix. The old `FABLE5_OPTIMIZER_` names remain temporary aliases for the version 3 transition.

## Remove

Remove a user-level skill with:

```bash
rm -rf -- "$HOME/.claude/skills/claude-model-optimizer"
```

Remove a project-local skill from the project root with:

```bash
rm -rf -- ".claude/skills/claude-model-optimizer"
```

For an always-on install, also edit `.claude/CLAUDE.md` and remove only the text between the `claude-model-optimizer:start` and `claude-model-optimizer:end` marker lines, including both markers. Keep the rest of the file.

Backups are not deleted automatically. Review them under `.claude/skill-backups/` or `~/.claude/skill-backups/` before removing them.

## Troubleshooting

### `git` is missing

The one-line installer uses Git to fetch the repository. Install Git, confirm `git --version` works, and rerun the command.

### The skill does not appear in Claude Code

Confirm that `SKILL.md` exists at the expected path, then open a new Claude Code session. Try invoking `/claude-model-optimizer` directly once.

### A project install went to the wrong directory

The project modes use the current working directory. Change to the project root before running the command, or set an explicit target:

```bash
CLAUDE_MODEL_OPTIMIZER_TARGET="/absolute/path/to/project" ./install.sh skill-project
```

### The installer reports a permissions error

Do not rerun it with `sudo`. Check ownership and permissions on the target `.claude` directory. A user install should write only inside your home directory, and a project install should write only inside that project.

### An existing skill was backed up

The installer found different content at the destination. It moved the old folder outside the skills directory so Claude Code does not load two copies with the same name. Compare the backup with the installed copy before deleting it.

## Installer modes

Run `./install.sh --help` for the current list:

| Mode | Result |
|---|---|
| `skill` | User-level on-demand skill. This is the default. |
| `skill-project` | Project-local on-demand skill. |
| `claude-md` | Project-local skill plus the always-on routing block. |
| `claude-md-print` | Print the generated routing block. Maintainers use this to keep the checked-in template synchronized. |

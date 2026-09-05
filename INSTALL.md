# Installation

Model Optimizer Lite uses one standalone skill package for Claude and Codex.
Claude invokes it with `/model-optimizer-lite`; Codex uses `$model-optimizer-lite`.

## Codex installation

From a checkout, run `./install.sh codex` for a user install or
`./install.sh codex-project` from the target project. Open a new Codex session
and invoke `$model-optimizer-lite`.

The targets are `~/.agents/skills/model-optimizer-lite/` and
`./.agents/skills/model-optimizer-lite/`. No Claude CLI, global model setting,
`AGENTS.md` edit, or always-on hook is required. Desktop use needs a local
skill-capable session; advice still works when CLI execution is unavailable.
The optional helper commands need Python 3.9+, and live model discovery needs a
standalone Codex CLI. Neither provider CLI is required to copy the skill files.

Rerun the same installer mode to update. Changed packages are backed up outside
skill discovery, under `.agents/skill-backups/`. Remove only the installed
`model-optimizer-lite` directory when uninstalling; review backups separately.
Do not delete other skills or provider state.

Set `MODEL_OPTIMIZER_LITE_CODEX_SKILLS_DIR` to override the user skills root, or
`MODEL_OPTIMIZER_LITE_TARGET` for a project target. `MODEL_OPTIMIZER_LITE_MODE` and
`MODEL_OPTIMIZER_LITE_REPO_URL` override mode and source.

## Claude installation

Set `MODEL_OPTIMIZER_LITE_CLAUDE_SKILLS_DIR` to override the user skills root.
For `claude-md` mode, `MODEL_OPTIMIZER_LITE_CLAUDE_MD` overrides the policy file
path; `MODEL_OPTIMIZER_LITE_TARGET` still selects the project skill location.

The default install adds Model Optimizer Lite to your Claude Code user skills. It works across projects and does not change any project files.

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
curl -fsSL https://raw.githubusercontent.com/nyldn/model-optimizer-lite/main/install.sh | bash
```

The installer copies the skill to:

```text
~/.claude/skills/model-optimizer-lite/
```

Confirm it is present:

```bash
test -f "$HOME/.claude/skills/model-optimizer-lite/SKILL.md" && echo "model-optimizer-lite is installed"
```

Open a new Claude Code session, then run:

```text
/model-optimizer-lite should Opus own this work, or does it need Fable?
```

## Inspect before installing

If you do not want to pipe a remote script into Bash, clone the repository and inspect the installer first:

```bash
git clone https://github.com/nyldn/model-optimizer-lite.git
cd model-optimizer-lite
./install.sh --help
./install.sh skill
```

## Install for one project

Run this from the project's root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/model-optimizer-lite/main/install.sh | bash -s -- skill-project
```

This writes the skill to:

```text
./.claude/skills/model-optimizer-lite/
```

Confirm it is present:

```bash
test -f ".claude/skills/model-optimizer-lite/SKILL.md" && echo "project skill is installed"
```

## Install the always-on router

Use this mode when you want a short routing policy loaded in every Claude Code session for one project. Run it from that project's root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/model-optimizer-lite/main/install.sh | bash -s -- claude-md
```

This mode makes two changes:

1. It installs the detailed skill at `.claude/skills/model-optimizer-lite/`.
2. It adds a managed block to `.claude/CLAUDE.md`.

The block starts and ends with these markers:

```html
<!-- model-optimizer-lite:start -->
<!-- model-optimizer-lite:end -->
```

The installer preserves everything outside that block. If the file changes, it writes a timestamped backup beside the original before replacing it. An incomplete managed block causes the installer to stop without changing the file.

## Update

Rerun the same command you used to install. The installer compares the installed files with the current repository and skips files that have not changed.

For the default user install:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/model-optimizer-lite/main/install.sh | bash
```

When an installed skill has local changes, the installer moves the old folder to `~/.claude/skill-backups/` for a user install or `.claude/skill-backups/` for a project install.

## Remove

Remove a user-level skill with:

```bash
rm -rf -- "$HOME/.claude/skills/model-optimizer-lite"
```

Remove a project-local skill from the project root with:

```bash
rm -rf -- ".claude/skills/model-optimizer-lite"
```

For an always-on install, also edit `.claude/CLAUDE.md` and remove only the text between the `model-optimizer-lite:start` and `model-optimizer-lite:end` marker lines, including both markers. Keep the rest of the file.

Backups are not deleted automatically. Review them under `.claude/skill-backups/` or `~/.claude/skill-backups/` before removing them.

## Troubleshooting

### `git` is missing

The one-line installer uses Git to fetch the repository. Install Git, confirm `git --version` works, and rerun the command.

### The skill does not appear in Claude Code

Confirm that `SKILL.md` exists at the expected path, then open a new Claude Code session. Try invoking `/model-optimizer-lite` directly once.

### A project install went to the wrong directory

The project modes use the current working directory. Change to the project root before running the command, or set an explicit target:

```bash
MODEL_OPTIMIZER_LITE_TARGET="/absolute/path/to/project" ./install.sh skill-project
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
| `codex` | User-level Codex skill under `~/.agents/skills/model-optimizer-lite/`. |
| `codex-project` | Project-local Codex skill under `.agents/skills/model-optimizer-lite/`. |

# Installation

AI Model Optimizer uses one standalone skill package for Claude and Codex.
Claude invokes it with `/ai-model-optimizer`; Codex uses `$ai-model-optimizer`.

## Codex installation

From a checkout, run `./install.sh codex` for a user install or
`./install.sh codex-project` from the target project. Open a new Codex session
and invoke `$ai-model-optimizer`.

The targets are `~/.agents/skills/ai-model-optimizer/` and
`./.agents/skills/ai-model-optimizer/`. No Claude CLI, global model setting,
`AGENTS.md` edit, or always-on hook is required. Desktop use needs a local
skill-capable session; advice still works when CLI execution is unavailable.
The optional helper commands need Python 3.9+, and live model discovery needs a
standalone Codex CLI. Neither provider CLI is required to copy the skill files.

Rerun the same installer mode to update. Changed packages are backed up outside
skill discovery, under `.agents/skill-backups/`. Remove only the installed
`ai-model-optimizer` directory when uninstalling; review backups separately.
Do not delete other skills or provider state.

Set `AI_MODEL_OPTIMIZER_CODEX_SKILLS_DIR` to override the user skills root, or
`AI_MODEL_OPTIMIZER_TARGET` for a project target. `AI_MODEL_OPTIMIZER_MODE` and
`AI_MODEL_OPTIMIZER_REPO_URL` override mode and source.

## Claude installation

Set `AI_MODEL_OPTIMIZER_CLAUDE_SKILLS_DIR` to override the user skills root.
For `claude-md` mode, `AI_MODEL_OPTIMIZER_CLAUDE_MD` overrides the policy file
path; `AI_MODEL_OPTIMIZER_TARGET` still selects the project skill location.

The default install adds AI Model Optimizer to your Claude Code user skills. It works across projects and does not change any project files.

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
curl -fsSL https://raw.githubusercontent.com/nyldn/ai-model-optimizer/main/install.sh | bash
```

The installer copies the skill to:

```text
~/.claude/skills/ai-model-optimizer/
```

Confirm it is present:

```bash
test -f "$HOME/.claude/skills/ai-model-optimizer/SKILL.md" && echo "ai-model-optimizer is installed"
```

Open a new Claude Code session, then run:

```text
/ai-model-optimizer should Opus own this work, or does it need Fable?
```

## Inspect before installing

If you do not want to pipe a remote script into Bash, clone the repository and inspect the installer first:

```bash
git clone https://github.com/nyldn/ai-model-optimizer.git
cd ai-model-optimizer
./install.sh --help
./install.sh skill
```

## Install for one project

Run this from the project's root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/ai-model-optimizer/main/install.sh | bash -s -- skill-project
```

This writes the skill to:

```text
./.claude/skills/ai-model-optimizer/
```

Confirm it is present:

```bash
test -f ".claude/skills/ai-model-optimizer/SKILL.md" && echo "project skill is installed"
```

## Install the always-on router

Use this mode when you want a short routing policy loaded in every Claude Code session for one project. Run it from that project's root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/ai-model-optimizer/main/install.sh | bash -s -- claude-md
```

This mode makes two changes:

1. It installs the detailed skill at `.claude/skills/ai-model-optimizer/`.
2. It adds a managed block to `.claude/CLAUDE.md`.

The block starts and ends with these markers:

```html
<!-- ai-model-optimizer:start -->
<!-- ai-model-optimizer:end -->
```

The installer preserves everything outside that block. If the file changes, it writes a timestamped backup beside the original before replacing it. An incomplete managed block causes the installer to stop without changing the file.

## Update

Rerun the same command you used to install. The installer compares the installed files with the current repository and skips files that have not changed.

For the default user install:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/ai-model-optimizer/main/install.sh | bash
```

When an installed skill has local changes, the installer moves the old folder to `~/.claude/skill-backups/` for a user install or `.claude/skill-backups/` for a project install.

## Remove

Remove a user-level skill with:

```bash
rm -rf -- "$HOME/.claude/skills/ai-model-optimizer"
```

Remove a project-local skill from the project root with:

```bash
rm -rf -- ".claude/skills/ai-model-optimizer"
```

For an always-on install, also edit `.claude/CLAUDE.md` and remove only the text between the `ai-model-optimizer:start` and `ai-model-optimizer:end` marker lines, including both markers. Keep the rest of the file.

Backups are not deleted automatically. Review them under `.claude/skill-backups/` or `~/.claude/skill-backups/` before removing them.

## Troubleshooting

### `git` is missing

The one-line installer uses Git to fetch the repository. Install Git, confirm `git --version` works, and rerun the command.

### The skill does not appear in Claude Code

Confirm that `SKILL.md` exists at the expected path, then open a new Claude Code session. Try invoking `/ai-model-optimizer` directly once.

### A project install went to the wrong directory

The project modes use the current working directory. Change to the project root before running the command, or set an explicit target:

```bash
AI_MODEL_OPTIMIZER_TARGET="/absolute/path/to/project" ./install.sh skill-project
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
| `codex` | User-level Codex skill under `~/.agents/skills/ai-model-optimizer/`. |
| `codex-project` | Project-local Codex skill under `.agents/skills/ai-model-optimizer/`. |

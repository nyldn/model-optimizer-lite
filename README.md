# Model Optimizer Lite

**Get help choosing which AI to use for the job, and when it is worth switching.**

Claude and Codex offer several AI models. Some suit everyday edits; others are
worth considering for a difficult bug or a major design decision. Picking the
most powerful one for everything can mean extra cost or waiting. Switching too
often means explaining your project all over again.

Model Optimizer Lite adds a small set of reusable instructions, called a *skill*,
to Claude or Codex. Ask it for help with a model choice, and it recommends a next
step with a reason. It covers both Claude and Codex models, including GPT-6 Astra.

## Why use it?

- **Spend less time choosing models.** Describe the work and get a recommendation
  about which available model to use and how much thinking effort to give it.
- **Avoid unnecessary switching.** If your current AI can finish the job and
  already understands the project, the guidance favors staying with it.
- **Get help when the work gets harder.** For a stubborn bug or a difficult design
  decision, it helps decide whether a more capable model would address the problem.
- **Repeat less when you switch.** It can prepare a short handoff with the goal,
  what has been tried, what has been checked, and what still needs an answer.
- **Make a second opinion useful.** It helps give another AI a specific review
  question and asks for findings that can be checked against the code.

The aim is less wasted time, repeated explanation, and unnecessary model use.
Cost and speed improvements have not been measured, so savings are not guaranteed.

## What does that look like?

| Your situation | How it helps |
| --- | --- |
| You need a small code change. | Helps choose a model suited to routine work without automatically reaching for the most powerful option. |
| You are halfway through a task and wonder whether to switch. | Weighs the benefit of switching against losing the context your current AI already has. |
| A bug is still unresolved. | Helps check whether the AI needs better information, better tools, or a more capable model. |
| Codex wrote a change and you want Claude to review it. | Prepares the relevant code, context, checks, and review question for the handoff. |

## How it works

You install the skill, then ask for it when you want help making one of these
decisions. You keep using Claude or Codex to do the actual work.

The skill gives advice. It cannot change the model in a running conversation by
itself. Where your app supports model selection or handing work to another AI,
you can use those controls to follow the recommendation. Otherwise, it explains
the manual step. Any model you explicitly choose takes priority.

There is no background service or extra AI subscription required by this project.
You still need access to the Claude or Codex models you want to use, with their
usual limits and charges. Installing the skill does not unlock additional models.

## Install: which app do you use?

### Claude chat or Cowork

1. [Download the skill ZIP](https://github.com/nyldn/model-optimizer-lite/releases/latest/download/model-optimizer-lite.zip). Keep it zipped.
2. In Claude, open **Customize → Skills → + → Create skill → Upload a skill** and choose the ZIP.
3. Enable the skill, start a new conversation, and ask: "Use Model Optimizer Lite to help me choose a model for this task."

Code execution must be enabled in Claude's settings. An organization may also
control whether you can upload skills. This installs the advice in Claude;
it does not give a cloud chat access to your local Codex CLI.
[Claude's upload instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

### Codex

Paste this into a local Codex coding session:

```text
$skill-installer install the skill from https://github.com/nyldn/model-optimizer-lite/tree/main/skills/model-optimizer-lite
```

Then ask:

```text
$model-optimizer-lite can my current model handle this task, or should I switch?
```

If the skill does not appear, start a new session. This uses Codex's built-in
skill installer. [OpenAI's instructions](https://learn.chatgpt.com/docs/build-skills).

For installation and updates through the native plugin manager instead, see
[native plugins](INSTALL.md#native-plugins). Choose one installation method per app
to avoid duplicate skills.

### Claude Code, or both coding apps

Paste this into your terminal. It installs for both Claude Code and Codex:

```sh
curl -fsSL https://github.com/nyldn/model-optimizer-lite/releases/latest/download/install.sh | bash -s -- both
```

For just one app, replace `both` with `claude` or `codex`. No Git, Python, or
separate provider CLI is needed to copy the skill. The terminal installer needs
Bash, curl, tar, and a SHA-256 tool, available on typical macOS/Linux systems.
Windows terminal users can use WSL; the Claude ZIP route needs no terminal.

The installer prints the version and checks the copied files. Open a new session
and use `/model-optimizer-lite` in Claude Code or `$model-optimizer-lite` in Codex
to confirm the app can find it. Installation does not change your model settings.

[Inspect the installer](install.sh) before running it if you prefer.
See [installation help](INSTALL.md) for project-only setup and other options.

### Update, check, or remove a terminal installation

Use the same command and change the words after `--`:

| Action | Words after `--` |
| --- | --- |
| Check installed files and version | `status both` |
| Download the current release and update installed copies | `update both` |
| Remove from both apps, keeping a recoverable backup | `uninstall both` |

For example:

```sh
curl -fsSL https://github.com/nyldn/model-optimizer-lite/releases/latest/download/install.sh | bash -s -- update both
```

The update command skips apps where the skill is absent. ZIP and native plugin
installations are managed in their respective apps; the terminal commands manage
direct local skill copies only.

## Optional tools for advanced use

You can skip this section to use the skill normally. These helper commands need
Python 3.9 or later. The first suggests a model for a difficult debugging task;
the second asks your installed Codex CLI which models it lists.

```sh
python3 shared/scripts/model_optimizer_lite.py route --host codex --task debugging --complexity hard
python3 shared/scripts/model_optimizer_lite.py codex-models
```

Neither command sends a task to an AI or changes your model settings. Listing
models briefly starts Codex, which may contact the provider and write its own
logs or caches. See the [helper documentation](shared/references/helper-commands.md)
for details and the separate tool for checking recorded review results.

That review tool checks whether a review finished and, where the output allows
it, which model actually ran. It does not prove the review is correct. Codex CLI
output may leave the model's identity unknown. The existing
[Fable review checks](shared/references/fable-review-gates.md) remain available
when you specifically require a Fable review.

## Relationship to the other optimizers

- [AI Environment Optimizer](https://github.com/nyldn/ai-env-optimizer) checks
  whether your installed AI tools and settings are set up correctly.
- Model Optimizer Lite helps you decide which model to use for the work in front of you.
- [Claude Octopus](https://github.com/nyldn/claude-octopus) handles larger
  workflows that coordinate several AI tools and reviewers.

You can use Model Optimizer Lite on its own. It borrows selected ideas from Octopus
without requiring an Octopus installation. The
[architecture notes](docs/architecture.md) explain which ideas were reused.

## Development

Edit `shared/`, then regenerate the standalone package:

```sh
python3 scripts/sync-packages.py
python3 scripts/build-distribution.py
./install.sh claude-md-print > claude-md/CLAUDE.md
tests/sync.sh
tests/install.sh
python3 -m unittest discover -s tests -p '*_test.py'
tests/codex-smoke.sh
tests/claude-smoke.sh
tests/fable-review-validator.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and
[CHANGELOG.md](CHANGELOG.md). MIT licensed.

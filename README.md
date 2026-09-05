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

## Quick start

Clone and inspect the installer:

```sh
git clone https://github.com/nyldn/model-optimizer-lite.git
cd model-optimizer-lite
./install.sh --help
```

Choose the app you use:

| App | Install | Type in a new session |
| --- | --- | --- |
| Claude | `./install.sh skill` | `/model-optimizer-lite` |
| Codex | `./install.sh codex` | `$model-optimizer-lite` |

Both apps use the same skill. Claude installs it under
`~/.claude/skills/model-optimizer-lite`; Codex uses
`~/.agents/skills/model-optimizer-lite`. You can install it for both.
Neither on-demand install edits model settings or project instructions.

Then ask in plain language, for example:

```text
$model-optimizer-lite can my current model handle this bug, or would Astra help?
$model-optimizer-lite prepare a handoff so Claude can review this change
/model-optimizer-lite which model should I use to update this database safely?
```

See [INSTALL.md](INSTALL.md) for project scope, updates, backups, and removal.
For a one-line Claude install:

```sh
curl -fsSL https://raw.githubusercontent.com/nyldn/model-optimizer-lite/main/install.sh | bash
```

## Desktop support

The install commands above are for local coding sessions that support skills.
Features differ between desktop chat, Cowork, coding sessions, and cloud sessions.
Installing this package does not add it to every chat window automatically.

The written guidance can still help you choose a model when an app cannot run
commands or switch models for you. In that case, follow the recommendation
manually and use the handoff text to carry the context into your next session.

You do not need a command-line tool to read and use the advice. The optional
helper that lists available Codex models needs a separately installed Codex CLI,
the command-line version of Codex.

See the [Codex profile](shared/references/codex-profile.md) and
[Claude profile](shared/references/claude-profile.md).

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

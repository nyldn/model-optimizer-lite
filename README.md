# AI Model Optimizer

A lightweight model-routing skill for Claude and Codex, including GPT-6 Astra.
It helps choose a model and effort, prepare a handoff, and verify a review result.

Either host can own the task. Keep a capable model already in context; escalate
when the work exposes a specific gap. The optional helpers make recommendations
and inspect evidence without dispatching inference.

## Quick start

Clone and inspect the installer:

```sh
git clone https://github.com/nyldn/ai-model-optimizer.git
cd ai-model-optimizer
./install.sh --help
```

Choose the host you use:

| Host | Install | Invoke in a new session |
| --- | --- | --- |
| Claude | `./install.sh skill` | `/claude-model-optimizer` |
| Codex | `./install.sh codex` | `$ai-model-optimizer` |

Both installations can coexist. Claude keeps its existing skill name and install
modes for compatibility. Codex installs under `~/.agents/skills/ai-model-optimizer`.
Neither on-demand install edits model settings or project instructions.

The former `nyldn/claude-model-optimizer` repository URL redirects to this project.
Existing local checkout directories do not need to move.

Examples:

```text
$ai-model-optimizer should this debugging task stay with Terra or escalate to Astra?
$ai-model-optimizer prepare a Claude review packet for this Codex implementation
/claude-model-optimizer choose a model and effort for this migration
```

See [INSTALL.md](INSTALL.md) for project scope, updates, backups, and removal.
The existing one-line Claude installer remains supported:

```sh
curl -fsSL https://raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh | bash
```

## What it does

- Shares routing and review policy across Claude and Codex.
- Preserves explicit model choices and considers the cost of moving context.
- Provides separate Claude and Codex/Astra guidance.
- Discovers Codex model IDs and supported effort levels through the native
  app-server, on demand, without submitting a prompt.
- Checks review completion and distinguishes requested from observed models.
- Keeps missing capabilities visible instead of silently falling back.

It has no daemon, required MCP server, scheduler, automatic reviewer fleet, or
mandatory paid router call. Native tools execute authorized work. A skill
recommendation by itself cannot switch a running model.

## Desktop support

Use the skill in a local coding session that supports skills. Ordinary Chat,
Cowork, local Code, and cloud sessions expose different tools and model controls.
When a session cannot execute commands or change its model, the skill gives a
recommendation and handoff instructions. Installing a CLI is unnecessary for
advice; the discovery helper needs a standalone Codex CLI.

See the [Codex profile](shared/references/codex-profile.md) and
[Claude profile](shared/references/claude-profile.md).

## Optional helpers

Python 3.9+ is required only for helpers and development checks.

```sh
python3 shared/scripts/model_optimizer.py route --host codex --task debugging --complexity hard
python3 shared/scripts/model_optimizer.py codex-models
```

These commands do not run inference or modify provider configuration. Discovery
starts a short-lived native process that may use account/network access and
write native logs or caches. [Command contracts](shared/references/helper-commands.md)
describe output, exit codes, timeouts, and privacy boundaries.

A Codex CLI review may complete without exposing authoritative model identity.
The receipt keeps that identity unverified. The existing
[Fable review gate](shared/references/fable-review-gates.md) remains available for
specifically requested Fable reviews.

## Relationship to the other optimizers

- [AI Environment Optimizer](https://github.com/nyldn/ai-env-optimizer) diagnoses
  installed tools and configuration.
- AI Model Optimizer chooses how to use available models.
- [Claude Octopus](https://github.com/nyldn/claude-octopus) handles larger
  multi-provider workflows, councils, and orchestration.

This project reuses selected Octopus design patterns without depending on its
runtime. [Architecture and reuse notes](docs/architecture.md) identify the source
patterns and what remains outside this project's scope.

Routing defaults are hypotheses. No cost or performance savings are claimed
without representative task evaluations.

## Development

Edit `shared/`, then regenerate the two standalone packages:

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

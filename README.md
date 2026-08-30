# Claude Model Optimizer

[![Test](https://github.com/nyldn/claude-model-optimizer/actions/workflows/test.yml/badge.svg)](https://github.com/nyldn/claude-model-optimizer/actions/workflows/test.yml)
[![Latest release](https://img.shields.io/github/v/release/nyldn/claude-model-optimizer)](https://github.com/nyldn/claude-model-optimizer/releases/latest)
[![License: MIT](https://img.shields.io/github/license/nyldn/claude-model-optimizer)](LICENSE)

A Claude Code skill for deciding when work belongs with Claude Opus 5, Claude Fable 5, or Codex/GPT-5.6.

Opus 5 owns everyday complex work. Fable 5 handles the hardest judgment gaps and can coordinate large sets of independent tasks. Codex provides a separate implementation and review path.

## Quick start

You need Claude Code, Git, curl, and Bash on macOS, Linux, or Windows through WSL.

1. Install the skill for your user account:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/nyldn/claude-model-optimizer/main/install.sh | bash
   ```

2. Confirm the skill exists:

   ```bash
   test -f "$HOME/.claude/skills/claude-model-optimizer/SKILL.md" && echo "claude-model-optimizer is installed"
   ```

3. Open a new Claude Code session and try it:

   ```text
   /claude-model-optimizer should Opus own this migration, or does it need Fable?
   ```

The default mode does not edit a project's `CLAUDE.md`. Its persistent files stay under `~/.claude/`.

See [INSTALL.md](INSTALL.md) for project-local installation, the always-on router, updates, removal, and troubleshooting.

## What it gives you

- A routing table based on the actual bottleneck in the work.
- Effort guidance for Opus, Fable, and the GPT-5.6 family.
- Independent Codex review, implementation, and runtime-verification patterns.
- A bounded Fable-led delegation pattern for work that divides cleanly.
- A model-verified Fable review gate for plans and release candidates.
- Small pilots, worker limits, progress stops, and task-level cost tracking.
- Workspace-limited safety defaults for agentic execution.

## Pick an install scope

| Scope | Command | What changes |
|---|---|---|
| Your user account | `./install.sh skill` | Adds the on-demand skill under `~/.claude/skills/`. This is the default. |
| Current project | `./install.sh skill-project` | Adds the on-demand skill under the current project's `.claude/skills/`. |
| Current project, always on | `./install.sh claude-md` | Adds the project skill and a small managed block in `.claude/CLAUDE.md`. |

Run `./install.sh --help` to see every mode. You can also ask Claude Code to install the repository:

```text
Install this skill: https://github.com/nyldn/claude-model-optimizer
```

Re-running the installer is a no-op when the installed files match. It moves changed skill folders to `~/.claude/skill-backups/` for a user install or `.claude/skill-backups/` for a project install before replacing them. The always-on mode preserves instructions outside its marked block and backs up a changed `CLAUDE.md` first.

## How routing works

| Work | Start with |
|---|---|
| Complex coding, planning, debugging, review, or enterprise workflows | Opus 5 |
| Highest-capability judgment, unusually ambiguous architecture, or a problem Opus cannot resolve | Fable 5 |
| Many independent, verifiable packets or source material too large for one useful context | Fable 5 coordinating workers that meet the acceptance criteria |
| Independent technical review, context scouting, alternative implementation, or runtime automation | Codex/GPT-5.6 Sol |
| Routine or high-volume work | The cheapest capable model already in context |

This table is a starting point. For repeated work, compare models on the same prompts, artifacts, checks, total task cost, and rework.

## Fable review gates

Use a Fable gate when a plan, architecture decision, or release candidate exists but still carries a hard judgment risk. Keep the review read-only. Pin the artifact and checkout, select Fable explicitly, verify Fable on the final assistant event of a completed run, and require an `APPROVE` or `REVISE` verdict.

After `REVISE`, the primary owner checks each finding against source and records it as accepted, rejected, or deferred. The next round receives the prior report, that resolution ledger, and the exact changed artifact. Stop after three rounds, or sooner if two rounds make no progress.

The [Fable review-gate template](skills/claude-model-optimizer/references/fable-review-gates.md) includes a restricted CLI command, result validation, prompt contract, and worker-identity checks.

## Fable-led delegation

Use Fable as a coordinator when the task splits into independent packets with objective checks, or when the input is too large for one useful context. Fable keeps responsibility for decomposition, unresolved judgment, and final integration. Codex workers receive bounded packets rather than authority over the whole task.

Pilot on a small slice with fewer than five workers. Do not add another worker layer. Isolate concurrent editors and stop after two rounds without progress. Record the model, effort, tokens, elapsed time, checks, and rework for each packet.

Claude dynamic workflows spawn Claude sessions. Codex participates through MCP or a thin Claude wrapper around the authenticated Codex CLI. A worker label does not switch providers by itself.

## Example requests

```text
/claude-model-optimizer have GPT-5.6 Sol independently review this Opus implementation
/claude-model-optimizer decide whether Fable should coordinate Sol, Terra, or Luna workers for this migration
/claude-model-optimizer prepare a compact context packet before escalating this architecture decision
/claude-model-optimizer verify the running checkout flow with Codex browser automation
```

Claude Code can also load the skill when a request asks about model ownership, effort selection, cross-model work, or local runtime verification.

Codex is optional. Without an installed and authenticated Codex CLI, the Claude routing guidance still works.

## Documentation

- [Installation and maintenance](INSTALL.md)
- [Change history](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Code of conduct](CODE_OF_CONDUCT.md)

## Design sources

The policy draws on current provider documentation:

- Anthropic's [Claude model selection guide](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- Anthropic's [cost and intelligence optimization guide](https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence)
- Anthropic's [Fable 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- Anthropic's [Opus 5 prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- Anthropic's [Claude 5 context-engineering guidance](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
- Anthropic's [Claude Code skills guide](https://code.claude.com/docs/en/skills)
- Anthropic's [dynamic workflow guide](https://code.claude.com/docs/en/workflows)
- OpenAI's [reasoning-model guidance](https://developers.openai.com/api/docs/guides/reasoning)
- OpenAI's [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model)
- OpenAI's [Codex sandbox documentation](https://learn.chatgpt.com/docs/sandboxing)

Provider pricing, retention rules, model behavior, and subscription limits change. Check the current terms before making compliance or purchasing decisions.

## License

MIT. See [LICENSE](LICENSE).

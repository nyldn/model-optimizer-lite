# Fable 5 Optimizer

Claude Code guidance for routing work across Claude Opus 5, Claude Fable 5, and Codex/GPT-5.6 Sol.

The default has changed: Opus 5 is now the everyday Claude Code lead for complex, mergeable work. Fable 5 is the escalation tier for the hardest capability and judgment gaps. Codex is a frontier peer for independent review, context gathering, alternative execution, and runtime verification—not merely a cheap mechanical worker.

The project ships as an on-demand Claude Code skill plus an optional lightweight `CLAUDE.md` policy.

## What You Get

- A routing matrix for choosing Opus, Fable, or Codex by the actual bottleneck.
- Effort guidance that starts Opus and Fable at `high` and raises effort only when the task warrants it.
- Cross-model patterns that prefer one capable owner and add reviewers only for a distinct job.
- A qualified Fable-led delegation pattern for work that genuinely benefits from independent workers.
- Small-slice pilots, worker limits, progress stops, and task-level cost tracking for dynamic workflows.
- A compact context-packet pattern for state that is genuinely scattered.
- Current Codex CLI templates for read-only review, bounded implementation, and browser/computer-use verification.
- Workspace-limited safety defaults for agentic execution.

## Install

| Mode | Pick this if |
|---|---|
| On-demand skill (default) | You want routing guidance loaded only when a task mentions these models or asks who should own the work. Installs per user and works across projects. |
| Project-local skill | You want the same on-demand behavior in one repository. |
| Always-on router | You want a short routing policy active in every session. This also installs the detailed project-local skill so Claude can load the mechanics only when needed. |

### On-Demand Skill

Ask Claude Code:

```text
install this skill https://github.com/nyldn/fable5-optimizer
```

Or install from the shell:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/fable5-optimizer/main/install.sh | bash
```

From a cloned copy:

```bash
./install.sh
```

The default install writes to `~/.claude/skills/fable5-optimizer`. A changed skill folder is backed up to `~/.claude/skill-backups/` first, a sibling of the skills root rather than a folder inside it, so Claude Code never discovers the backup as a second skill with the same name. Project-local installs use `.claude/skill-backups/` in the project. Reinstalling an unchanged version does nothing and leaves no backup.

For a project-local install:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/fable5-optimizer/main/install.sh | bash -s -- skill-project
```

### Always-On Router

Run from the target project root:

```bash
curl -fsSL https://raw.githubusercontent.com/nyldn/fable5-optimizer/main/install.sh | bash -s -- claude-md
```

Or from a cloned copy:

```bash
./install.sh claude-md
```

This mode:

1. installs the detailed skill to `.claude/skills/fable5-optimizer/`
2. writes a managed routing block to `.claude/CLAUDE.md`

The managed block is intentionally lightweight. Re-running the installer replaces the block rather than stacking copies, preserves unrelated project instructions, and backs up existing files first. When nothing would change, the rerun is a byte-for-byte no-op and writes no backup.

Markers are matched as whole lines, so prose that merely mentions them is left alone. If a file opens a managed block without closing it, the installer refuses rather than guessing where the block ends. A symlinked `CLAUDE.md` is written through, so a dotfiles-managed file keeps its indirection. `CLAUDE.md` is written with your umask default.

## Default Routing

| Work | Start with |
|---|---|
| Complex coding, planning, debugging, review, or enterprise workflows | Opus 5 |
| Highest-capability judgment, unusually ambiguous architecture, or a problem Opus cannot resolve | Fable 5 |
| Many independent, verifiable packets, an input too large for one context, or a measured pattern of unusually expensive routine-work failures | Fable 5 coordinating the cheapest workers that meet the acceptance criteria |
| Independent technical review, context scouting, alternative implementation, or runtime automation | Codex/GPT-5.6 Sol |
| Routine or high-volume work | The cheapest capable model already in context |

Use the table as a starting point, not a guarantee. For repeated workflows, evaluate models on your actual prompts, artifacts, acceptance criteria, total task cost, and rework.

## Fable-led delegation

Use Fable as a coordinator when the task splits into independent packets with objective checks, or when the input is too large for one useful context. Keep Fable responsible for decomposition, unresolved judgment, and final integration. Codex workers receive bounded packets rather than authority over the whole task.

Start with fewer than five workers on a small slice. Keep workers from creating another agent layer, isolate concurrent editors, and stop after two rounds without progress. Record model, effort, tokens, elapsed time, checks, and rework for each packet. If one model at lower effort clears the same acceptance bar, the single-model run is the better route.

Claude dynamic workflows spawn Claude sessions. Codex participates through MCP or a thin Claude wrapper around the authenticated Codex CLI. The worker label alone does not switch providers.

## Usage Examples

```text
/fable5-optimizer should Opus own this migration, or does it need Fable?
/fable5-optimizer have GPT-5.6 Sol independently review this Opus implementation
/fable5-optimizer decide whether Fable should coordinate Sol, Terra, or Luna workers for this migration
/fable5-optimizer prepare a compact context packet before escalating this architecture decision
/fable5-optimizer verify the running checkout flow with Codex browser automation
```

Claude Code can also load the skill automatically when a request is about Opus/Fable/Codex routing, effort selection, cross-model orchestration, or local runtime verification.

## Requirements

- Claude Code with skills support.
- Codex CLI, installed and authenticated, for Codex delegation.

Check both:

```bash
claude --version
codex --version
```

Without Codex, the Claude routing guidance still works.

## Design Basis

The current policy is grounded in:

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

Provider pricing, retention rules, model behavior, and subscription limits change quickly. Verify current terms before making compliance or procurement decisions.

## Versioning

Releases follow semantic versioning and are tagged `vX.Y.Z`. History lives in [CHANGELOG.md](CHANGELOG.md).

## Contributing

Keep changes focused on routing policy. Put invocation-only detail under `skills/fable5-optimizer/references/` so the always-loaded context stays small.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

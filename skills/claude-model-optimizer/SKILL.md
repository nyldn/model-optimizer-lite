---
name: claude-model-optimizer
description: Load before answering whenever a request mentions Claude Opus 5, Claude Fable 5, GPT-5.6 Sol, Terra, or Luna, Codex, or asks which model or agent should plan, implement, review, research, or verify work. Use for model routing, cross-model and dynamic workflows, Codex delegation, effort selection, context preparation, cost controls, and runtime/browser verification. Do not use for ordinary implementation or review with no model-choice question, or for generic prompt rewriting.
---

# Claude Model Optimizer

Route work across Claude Opus 5, Claude Fable 5, and Codex/GPT-5.6 Sol without turning every task into a multi-model ceremony.

## Default Policy

Start complex Claude Code work with **Opus 5 at `high` effort**. It is the everyday default for planning, production implementation, debugging, code review, knowledge work, and agentic tool use.

Escalate to **Fable 5** when the task needs Anthropic's highest available capability: unusually ambiguous architecture, the hardest long-horizon work, deep or obscure knowledge, or a judgment call where Opus has exposed a real capability gap.

Use **Codex/GPT-5.6 Sol** as a frontier peer when an independent perspective, a different tool harness, large-context evidence gathering, persistent execution, or browser/computer-use automation is useful. It is not limited to throwaway scripts, and its output is evidence rather than authority.

Prefer one capable model end to end when that is enough. Add another model only when it has a distinct job.

For large work that splits into independent packets, Fable 5 can coordinate bounded workers while retaining planning and integration judgment. Use this as a measured exception to the one-owner default, not as a standing swarm.

## Model Roles

| Model | Default role | Reach for it when | Watch for |
|---|---|---|---|
| Opus 5 | Everyday Claude Code lead | Complex coding, planning, refactors, enterprise work, visual tasks, review, and multi-step execution | Over-verification, scope expansion, verbose narration, unnecessary subagents |
| Fable 5 | Capability escalation | Highest-stakes judgment, novel or deeply ambiguous problems, hardest long-running agents, obscure knowledge | Cost, latency, safety-classifier fallbacks, and data-retention constraints |
| GPT-5.6 Sol through Codex | Independent frontier executor and reviewer | Fresh-context review, technical edge cases, research/context scouting, tool-heavy execution, runtime verification | Broad diffs if the boundary is vague; destructive risk when the execution environment is too permissive |

These are routing heuristics, not personality guarantees. Model behavior varies by harness, effort, tools, and task. For repeated work, compare models on the user's real prompts and acceptance criteria.

## Routing Gate

Route by the bottleneck:

| Work type | Start with |
|---|---|
| Routine lookup, classification, or small rewrite | The cheapest capable model already in context |
| Production coding, debugging, refactoring, code review, or business workflow | Opus 5 |
| Architecture, product judgment, API design, UX taste, or user-facing copy | Opus 5; escalate to Fable 5 when ambiguity or stakes justify it |
| Highest-capability research or a problem Opus has failed to resolve | Fable 5 |
| Many independent, verifiable work packets, an input too large for one context, or a measured pattern of unusually expensive routine-work failures | Fable 5 coordinator with the cheapest workers that meet the acceptance criteria; pilot on a small slice first |
| Independent code review, edge-case search, context gathering, or alternative implementation | Codex/GPT-5.6 Sol, then the primary Claude session verifies |
| Browser, app, simulator, screenshot, or computer-use verification | Whichever harness has the best local automation; Codex is often a strong route |
| Deterministic bulk edits or data processing | The cheapest capable execution model; Codex is often suitable |

Treat API/schema contracts, security-sensitive work, release artifacts, destructive migrations, and user-facing UI as risk surfaces. Keep final judgment in the primary Claude session and escalate to Fable when the unresolved risk is genuinely capability- or judgment-bound.

## Effort Discipline

- **Opus 5:** start at `high`. Use `low` or `medium` when evals show quality holds; use `xhigh` for demanding coding or agentic work. Do not default to `max`.
- **Fable 5:** start at `high`; use `xhigh` only for the most capability-sensitive work and lower effort for routine tasks.
- **GPT-5.6 family:** start with the Codex configured default. Use lower-cost family members for routine, high-volume packets when they pass the same checks. Sol `high` is a reasonable trial for capability-sensitive implementation. Reserve `max` for cases where representative evaluations beat `high` or `xhigh` after accounting for latency, tokens, and rework.

Effort is a tuning knob, not a substitute for a clear task or a way to extend run duration. Compare total task cost, latency, context use, tool calls, and rework—not token sticker prices alone.

## Context And Handoffs

Before a cross-model handoff, state:

- the exact task and intended outcome
- relevant files, diff, artifact, or runtime target
- checkable acceptance criteria
- scope boundaries and actions that require approval
- known decisions, gaps, and validation already run

Use active context when it already contains the state. When state is scattered across files, diffs, screenshots, or prior decisions, have Codex assemble a compact context packet before an expensive judgment pass. Keep it to roughly a page: ask, current state, evidence, decisions, gaps, and the exact judgment requested.

Do not create a packet for a small task or repeat facts the receiving model can cheaply inspect.

## Multi-Model Patterns

### Default: one capable owner

Let Opus 5 plan, implement, and verify the task. This is the right path for most mergeable work.

### High-stakes split

Use only the stages that add value:

1. Opus 5 produces the plan or implementation.
2. Codex reviews from fresh context for concrete bugs, edge cases, and missing verification.
3. Fable 5 reviews only the remaining architecture, taste, or capability-sensitive question.
4. The primary Claude session verifies findings against the artifact and resolves conflicts.

Do not require all three models for every task. Reciprocal reviews are useful for calibrating a new model or resolving real disagreement, not as a standing ritual.

### Fable review gate

Use Fable as a bounded read-only gate when an existing plan, architecture decision, or release candidate still carries a capability-sensitive judgment risk. Keep mechanical implementation and verification with the primary owner.

Before the run, pin the exact artifact, checkout, revision, review questions, allowed tools, and response contract. Explicitly select Fable and verify the actual model metadata in the completed result. A fallback model, a worker label, or a run that stops after tool use without a final verdict is not a completed Fable review.

Require `APPROVE` or `REVISE`, concrete evidence for every blocker, and a scope check. The primary owner independently reproduces each finding and records it as accepted, rejected, or deferred in a resolution ledger. A revision prompt includes the prior report, that ledger, and the exact changed artifact or diff. Ask Fable to check closure first, then inspect changed seams for new blockers.

Use at most three revision rounds for one named gate. Fewer blockers or verified closures count as progress; two rounds with no progress trigger the existing stop rule. If the third round still returns `REVISE`, return the unresolved findings to the owner instead of looping.

Read [references/fable-review-gates.md](references/fable-review-gates.md) only when preparing or validating a Fable review gate.

### Context scout

Codex can gather repository state, relevant source material, logs, and test evidence. Ask for a factual packet, not a decision disguised as a summary. The judgment model should receive sources and acceptance criteria without the maker's preferred conclusion.

### Fable-led delegation

Use Fable 5 as the coordinator only when at least one of these conditions holds:

- the task divides into independent, verifiable work packets
- the source material exceeds one model's useful context
- routine workers have a measured pattern of unusually expensive failures that cheaper workers can contain

Before building the workflow, compare a single capable model across effort levels. If one model at lower effort meets the acceptance bar, use it. Delegation adds planning, handoff, review, and merge costs that do not pay back on one dependent chain.

When delegation qualifies:

1. Fable defines each packet's outcome, inputs, dependencies, acceptance criteria, and protected boundaries.
2. Route each packet to the cheapest worker that has cleared the same checks on representative work. Keep Codex at its configured default unless a task-specific evaluation supports another model or effort level.
3. Fable resolves cross-packet conflicts and performs final integration. Add an independent reviewer only for a named risk or uncertainty.

Pilot on a small slice with fewer than five workers. Do not let workers spawn another layer by default. Isolate concurrent editors in worktrees, and stop when two consecutive rounds make no progress. Record the task, model, effort, tokens, elapsed time, checks, and rework so "cheaper" means lower cost per accepted result rather than lower sticker price or slower depletion of one subscription.

After workers start, inspect the actual model metadata when the harness exposes it. Claude subagents can inherit the session's default model. If the workflow cannot pin or verify a worker model, plan and report it as the inherited model rather than claiming the cheapest capable worker ran.

Claude dynamic workflows spawn Claude sessions. To use Codex as the real worker, expose it through MCP or a thin Claude wrapper that calls the authenticated Codex CLI. Keep that transport detail out of the worker's decision rights.

## Prompt Discipline For Claude 5

- Give the goal, why it matters, constraints, and output contract. For implementation, provide the complete specification up front.
- Keep instructions brief and avoid repeating the same rule across `CLAUDE.md`, skills, prompts, and tool descriptions.
- Let the model use judgment for routine choices. Constrain scope when different interpretations would materially change the work.
- Opus 5 already self-corrects and verifies. Remove blanket "double-check everything" steps or mandatory verifier subagents unless the workflow has a specific independent-verification need.
- State desired response or document length explicitly; effort controls thinking, not visible verbosity.
- For long-document analysis, place the source material before the question. When factual precision matters, ask for relevant extracts and ground the analysis in them.
- Do not ask a model to reveal or reproduce hidden reasoning. Ask for conclusions, evidence, tradeoffs, or a concise rationale.
- Remove legacy anti-laziness prompts, token countdowns, aggressive all-caps triggers, and micromanaged step lists.

## Safety And Data Boundaries

- Use a read-only sandbox for review and evidence gathering.
- For edits, prefer a workspace-limited sandbox. Expand writable roots only to named targets.
- Do not use full-device access as the default. Require user authority for destructive, irreversible, account-changing, or externally consequential actions.
- Isolate parallel implementers in separate worktrees.
- Data governance overrides capability routing. Verify current provider retention and compliance terms before sending restricted data; do not infer them from model quality or subscription access.

## Codex Workflows

Read [references/codex-workflows.md](references/codex-workflows.md) only when actually invoking Codex, creating a Codex wrapper, or checking the CLI command patterns. It contains the shared report contract plus review, implementation, runtime-verification, and workflow-wrapper templates.

## Reporting

Lead with the outcome. Say which model handled which distinct job, cite concrete files/checks/evidence, and identify anything not verified. If another model found no issues, name the reviewed target and report that result plainly.

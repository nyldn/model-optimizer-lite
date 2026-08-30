# Model Routing

Use **Claude Opus 5 at `high` effort** as the everyday default for complex Claude Code work: planning, production implementation, debugging, review, knowledge work, and agentic tool use.

Escalate to **Claude Fable 5** when the work genuinely needs Anthropic's highest available capability: unusually ambiguous architecture, the hardest long-horizon task, deep or obscure knowledge, or a judgment gap Opus has exposed.

Use **Codex/GPT-5.6 Sol** as a frontier peer for a distinct job: fresh-context technical review, context and evidence gathering, alternative implementation, persistent execution, or browser/computer-use verification. Treat its output as evidence that the primary Claude session must verify, not as final authority.

Prefer one capable owner end to end. Add another model only when it contributes a different capability or independent perspective; do not run a three-model loop by default.

For large work that splits into independent, verifiable work packets, Fable 5 may coordinate while Codex handles bounded packets and Fable retains integration judgment. Pilot on a small slice, keep the first run below five workers, avoid nested worker fan-out, and stop after two rounds without progress. Use one model at lower effort instead when the work is a dependent chain or fits comfortably in one context.

When a task explicitly requires Fable, pin the model and verify the actual model metadata in a normally completed result. A silent fallback or a run that stops without a final verdict does not satisfy a Fable gate. On revision, carry forward the prior report and a resolution ledger; stop after three rounds or two rounds without progress.

Before delegating, state the task, relevant files or artifact, checkable acceptance criteria, scope boundaries, and validation already run. Keep prompts brief and self-contained. Use a compact context packet only when state is genuinely scattered.

Keep reviews read-only and implementation sandboxes workspace-limited. Expand access only to named targets, isolate parallel edits in worktrees, and pause for destructive, irreversible, or externally consequential actions.

For detailed routing, effort guidance, prompt patterns, and current Codex command templates, load `/fable5-optimizer`.

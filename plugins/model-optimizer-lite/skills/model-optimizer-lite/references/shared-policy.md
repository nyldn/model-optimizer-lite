# Shared routing policy

The owner is the active session with the context and authority to finish the task.
Either Claude or Codex can own planning, implementation, review, and integration.
The other provider is an optional peer, never a mandatory approval authority.

## Decision order

1. Honor explicit user pins and constraints. A model unavailable to the account
   requires a disclosed alternative, not a silent substitution.
2. Keep a capable model already in context. Include handoff and rework costs when
   considering a cheaper model.
3. For a fresh task, choose a host-supported model for its bottleneck: routine
   execution, difficult reasoning, long-running tool use, or independent review.
4. Begin with the host's configured effort. Raise or lower it only for a reason
   tied to the task or representative results. Effort names differ by client.
5. Escalate when an unresolved capability gap remains after inspecting evidence.
   Fix missing tools, context, or acceptance criteria before buying more reasoning.

Available models are constrained by client version, sign-in method, rollout,
organization policy, and execution host. A catalog entry is inventory, not proof
that an authenticated inference request will succeed. Never probe availability by
running an expensive task or forwarding restricted data without authority.

## Context packets

Use a packet only when moving work into another context. Include the intended
outcome, authoritative checkout and revision, relevant evidence, constraints,
decisions already made, completed checks, and the exact unresolved question.
Preserve the original goal when incorporating follow-up instructions.

## Selective independent review

Run deterministic checks before asking a model to review. Choose a fresh reviewer
for a named risk. A different provider can add useful diversity, but a second
review must earn its setup and verification cost. Require reproducible findings,
then accept, reject, or defer each one with evidence. Review the changed revision
and closure of earlier findings instead of restarting an identical full review.

## Bounded delegation

Delegate only independent, verifiable packets when authorization and available
tools support it. Keep one owner, a small initial worker set, and one worker
layer. Isolate concurrent editors. Stop after two consecutive rounds without
progress and inspect the cause. Labels do not select worker models.

## Evaluation

Trial the same representative tasks and acceptance checks with alternative routes.
Record model, effort, completion, elapsed time, reported usage, checks, and user
corrections. Compare cost per accepted result. Treat unknown usage as unknown;
subscription credits and API prices are different accounting systems.

The deterministic router is a starting policy. It does not infer task difficulty
from private transcripts, predict prices, measure capability, or prove savings.

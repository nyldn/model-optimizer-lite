# Provider-neutral review gates

Use a gate only when a named artifact has an unresolved question worth independent
judgment. Run deterministic checks first. Pin the checkout, revision, artifact,
review question, permissions, and chosen model before dispatch.

The reviewer returns:

```text
VERDICT: APPROVE or REVISE

BLOCKERS
- Finding, evidence path and line, concrete failure, smallest correction

NONBLOCKING
- Evidence-backed suggestions and remaining verification gaps
```

Use the native host or a narrowly scoped authenticated CLI. Claude's final
assistant model can establish identity when emitted in its event stream. Codex
CLI completion events alone cannot. See [receipt validation](helper-commands.md).
Record requested and observed model separately; leave unavailable metadata empty.
No receipt or reviewer verdict authorizes a merge, release, or deployment.

The primary owner reproduces findings and records accepted, rejected, or deferred
dispositions with evidence. On revision, send the previous report, disposition
ledger, and exact changed artifact. Ask for closure first, then new problems at
changed boundaries. Use at most three rounds and stop after two without progress.

Keep one reviewer by default. Add provider diversity for a distinct uncertainty,
not to increase the number of findings. Keep failed, interrupted, fallback, and
model-unverified runs visible as those outcomes. No silent approval or retry loop.

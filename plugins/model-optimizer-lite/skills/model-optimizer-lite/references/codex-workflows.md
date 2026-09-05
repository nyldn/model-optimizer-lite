# Codex Workflows

Load this reference only when the task will actually invoke Codex or build a wrapper around it.

## Before Running Codex

1. Check the worktree and preserve user changes.
2. Define the task boundary, acceptance criteria, and what must not change.
3. Use `codex exec` for noninteractive work. Bare `codex "prompt"` opens the interactive TUI.
4. Keep the prompt brief and self-contained.
5. Use the narrowest useful sandbox. Do not bypass approvals and sandboxing unless the run is already isolated by an external environment and the user has authorized that scope.

Let Codex use its configured model unless the user or authorized workflow selects
another available model. Preserve exact pins, including Astra. For example, to
pin Sol, add:

```bash
--model gpt-5.6-sol
```

## Report Contract

Every delegated run should report:

- status: done, blocked, found issues, or no issues
- files changed or reviewed
- checks run and results
- evidence paths: reports, logs, screenshots
- blockers, gaps, or skipped verification

## Independent Review

Use Codex as a second reviewer when another perspective is worth the setup cost.
The primary owner inspects every cited finding, whether that owner uses Claude
or Codex.

For uncommitted changes:

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fable5-review.XXXXXX")"
REPORT="$REPORT_DIR/report.md"
codex review --uncommitted > "$REPORT"
```

For a branch diff:

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fable5-review.XXXXXX")"
REPORT="$REPORT_DIR/report.md"
codex review --base main > "$REPORT"
```

Plain `codex review` is best for a standard review. When the review needs a specific focus or an explicit read-only boundary, use:

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fable5-review.XXXXXX")"
REPORT="$REPORT_DIR/report.md"
codex exec -C "$PWD" --sandbox read-only -o "$REPORT" "Review <the uncommitted changes | the diff against <base>> for <focus>. Prioritize findings over summary: severity, file/line reference, concrete failure mode, and fix direction. Do not edit files. If there are no substantive findings, say so and name residual test gaps."
```

After the run:

- inspect each cited file or diff
- confirm findings before presenting them
- separate confirmed issues from unverified suggestions
- if the review is clean, say so and name the target; do not rerun merely to manufacture findings

## Bounded Implementation

Use Codex when the intended behavior is clear and the result is independently checkable.

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fable5-implementation.XXXXXX")"
REPORT="$REPORT_DIR/report.md"
codex exec -C "$PWD" --sandbox workspace-write -o "$REPORT" "Implement this bounded change. Preserve surrounding style and keep the diff scoped.

Task:
<exact task>

Acceptance criteria:
- <criterion>

Do not perform destructive git operations or unrelated refactors. Run relevant lightweight checks. Report status, files changed, checks, evidence, and blockers."
```

After Codex edits:

- review the diff before reporting success
- run important checks it skipped
- fix small misses directly when that is faster than another delegation
- use a separate worktree for each parallel implementer

## Runtime And Computer-Use Verification

Use this route for browser automation, screenshots, simulators, desktop app inspection, or a running UI.

```bash
REPORT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fable5-runtime.XXXXXX")"
REPORT="$REPORT_DIR/report.md"
codex exec -C "$PWD" --sandbox workspace-write --add-dir "$REPORT_DIR" -o "$REPORT" "Verify this runtime behavior with the available local browser, app-automation, or computer-use tools. Do not edit product source. Save screenshots or logs under $REPORT_DIR.

Target:
- URL/app:
- Flow:
- Expected result:
- Evidence needed:

Do not use secrets unless explicitly provided for this task. Do not make purchases, accept terms, delete data, change accounts, or take other externally consequential actions. Report status, environment, steps, evidence paths, and blockers."
```

Inspect screenshots or logs before repeating visual claims. A text-only success report is not sufficient evidence for a visual result.

If the required automation cannot run inside a workspace-limited sandbox, identify the exact missing permission. Do not silently jump to full access.

## Codex Inside Claude Workflows Or Subagents

Claude dynamic-workflow agents are Claude sessions. A label such as `sol:implement-auth` does not change the model behind that agent. To make Codex the real worker, expose it through an MCP tool or use one thin Claude wrapper that calls the authenticated Codex CLI.

For a qualified Fable-led delegation run:

- test the workflow on a small slice before applying it to the full target
- set `/config workflowSizeGuideline=small`, or otherwise keep the first run below five workers
- keep workers single-level by default; do not let a worker spawn another worker tree
- use the Codex configured default, then raise model or effort only when representative checks justify it
- isolate concurrent editors in separate worktrees
- stop when two consecutive rounds make no progress
- record each packet's model, effort, tokens, elapsed time, checks, and rework

The wrapper is transport, not a second planner:

- use a lightweight Claude model and effort level for wrapper-only duty
- label the wrapper by the real worker, for example `gpt-5.6-sol:review-auth`
- set an explicit timeout or run in the background and poll the report file
- do not add wrappers or parallel agents to small tasks
- pass the packet and acceptance criteria through without adding a preferred solution

The wrapper coordinates transport; it should not reinterpret the review before the primary session sees the evidence.

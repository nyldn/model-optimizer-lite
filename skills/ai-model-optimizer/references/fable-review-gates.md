# Fable review gates

Load this reference only when Fable will review an existing artifact at a named decision point.

## Use a gate for judgment

A Fable gate fits when:

- a plan or implementation already exists
- the remaining risk is architectural, product-sensitive, cross-system, or hard to reverse
- a read-only reviewer can cite evidence and return a checkable verdict
- the primary owner will verify and disposition every finding

Do not use Fable to return a fixed word, test whether a command launches, repeat an ordinary diff review, or replace deterministic checks. Use the cheapest available tool for those jobs.

## Prepare the review

Pin these inputs before launch:

- the artifact path and revision
- the authoritative checkout or worktree
- locked intent and protected boundaries
- the exact questions that need Fable-level judgment
- prior checks and known gaps
- allowed tools and prohibited actions
- the response contract below

Confirm that the selected tools can read every named source. If the run cannot access the checkout, provide a complete evidence packet or stop. Do not improvise through stale memory, a browser copy of local files, or an identical retry.

## Run and validate

This template keeps the review read-only and writes a machine-checkable result:

```bash
REVIEW_DIR="$(mktemp -d "${TMPDIR:-/tmp}/fable-review.XXXXXX")"
PROMPT="$REVIEW_DIR/prompt.md"
REPORT="$REVIEW_DIR/report.jsonl"

claude -p --model claude-fable-5 \
  --effort high \
  --restricted \
  --allowed-tools Read,Glob,Grep \
  --output-format stream-json \
  --verbose \
  < "$PROMPT" > "$REPORT"

jq -s -e '
  # fable-review-validator:start
  (map(select(.type == "result")) | last) as $result |
  (map(select(
    .type == "assistant" and
    (.message.content | any(.type == "text"))
  )) | last) as $final |
  (($final.message.content // []) |
    map(select(.type == "text") | .text) |
    join("\n")) as $final_text |
  $result.subtype == "success" and
  $result.is_error == false and
  $final.message.model == "claude-fable-5" and
  ($final_text | test("(?m)^VERDICT: (APPROVE|REVISE)$")) and
  ($result.result | test("(?m)^VERDICT: (APPROVE|REVISE)$"))
  # fable-review-validator:end
' "$REPORT"
```

The event-stream check verifies that Fable produced the final text-bearing assistant message. A label in the prompt or orchestration UI does not. Claude Code may list a small auxiliary model in aggregate usage metadata for session bookkeeping, so aggregate model keys alone cannot prove which model wrote the verdict. If the final assistant event reports another model, disclose the fallback and decide whether that result is useful, but do not call it a Fable review.

Normal completion requires a successful result object and a final verdict. A process that stops after tool use, times out, or produces no final report failed the gate. Retry only after changing the invocation, tool access, timeout, or evidence packet.

## Prompt contract

Put the source material before the review questions. End the prompt with this contract:

```text
Return:

VERDICT: APPROVE or REVISE

BLOCKERS
- Finding, evidence path and line, failure mode, smallest correction

NONBLOCKING
- Important improvement with evidence

CLARITY QUESTIONS
- Only questions source evidence cannot settle

SCOPE CHECK
- Whether the artifact stays within locked intent and authority

Do not edit files or perform external actions.
```

An approval means no unresolved blocker remains within the named gate. It does not authorize merge, release, deployment, or another external action.

## Disposition findings

The primary owner checks every finding against current source before changing anything. Record:

| Finding | Disposition | Verification | Correction or reason |
|---|---|---|---|
| Stable ID or short name | accepted, rejected, or deferred | File, command, test, or source check | Commit, diff, owner decision, or rejection evidence |

Do not silently drop nonblocking findings. Deferral needs an owner, reason, and later decision point.

## Revision rounds

For a revision round, provide:

- the prior Fable report
- the completed resolution ledger
- the corrected artifact or exact diff
- any source revision that changed

Ask Fable to verify closure of accepted findings first. Then ask it to inspect changed seams for new blockers. This keeps the review cumulative without limiting it to the previous list.

Use no more than three rounds for one named gate. A shrinking blocker set, verified closures, or an approval is progress. If two rounds make no progress, stop early. If round three still returns `REVISE`, give the unresolved ledger to the owner instead of starting a fourth round.

Save each prompt and report under a named, ignored evidence directory when the workflow spans sessions. Record the actual model, result, accepted findings, corrective revision, checks, and elapsed time.

## Coordinated workers

Fable may delegate independent evidence gathering, but keep the coordinator responsible for the verdict. Limit the first run to fewer than five workers and keep worker fan-out single-level.

Check actual worker model metadata after launch. Claude subagents may inherit the session default, including Opus. If the harness cannot pin or verify worker identity, report the inherited model and account for its cost. Do not describe an Opus worker as a cheaper worker merely because the task label says otherwise.

For a planned coordinator run, validate Fable as the final coordinator and validate every declared worker model separately, then report the result as coordinated rather than Fable-only.

Require every worker to return sources, checks, and gaps. If the coordinator is interrupted before synthesis, preserve worker reports as partial evidence, but the gate remains incomplete.

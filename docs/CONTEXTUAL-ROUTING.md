# Contextual routing

Version 6 uses `Stay`, `Delegate`, and `Switch`. It first filters by
user and project constraints, account availability, and execution-tool support.
Then it considers the remaining task, useful existing context, observed local
results, and comparable benchmark evidence. A better overall rank alone does
not justify moving a conversation or starting a child.

For example, if one model leads the coding-agent index but another leads its
repository Q&A component, a new repository question favors the latter. A patch
uses patch or terminal evidence instead. A short summary stays with the owner
who already investigated it. An independent concurrency check can go to one
child while the owner retains the full review context.

## Evidence boundaries

[Artificial Analysis coding agents](https://artificialanalysis.ai/agents/coding-agents)
measures a model with an agent setup and separates coding and repository Q&A
components. Its index is distinct from a coding model score returned by the
general model API. Match the component, model version, effort, and tool setup.
Do not substitute one for the other.

[Artificial Analysis intelligence methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking)
describes a weighted composite of different evaluations. Use the relevant
component for broad reasoning, rather than treating its overall number as a
coding-agent result. Benchmark versions matter when comparing scores.

[BullshitBench](https://github.com/petergpt/bullshit-benchmark) measures whether
models challenge invalid premises. It does not measure false rejection of valid
questions. A premise-checking route therefore needs checks of both valid and
invalid examples before being treated as reliable.

The skill consumes supplied or previously reviewed evidence, or browses a
relevant source when a consequential choice needs freshness. It ships no score
database or API client. Missing data stays uncertain; newer model versions do
not inherit older scores. Local accepted results take precedence over public
scores. No benchmark proves account access or subscription savings.

## Execution boundaries

For an active authorized task, the skill can automatically dispatch one bounded
child through a supported host tool. A model-choice question only requests
advice. Reviews default to read-only, have one question and a stopping condition,
and permit no recursive delegation or automatic retry. Authorized edits require
a file scope that avoids concurrent owner writes. The owner verifies the result.

[Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
and [Claude subagents](https://code.claude.com/docs/en/sub-agents) expose model
selection within their hosts. Neither establishes native access to the other
provider. Cross-provider execution requires an already-configured, verified tool
with the necessary model and permissions. Otherwise the skill reports an
unexecuted handoff and continues feasible owner work. It does not install an
adapter, run a provider CLI implicitly, or copy authentication or agent homes.

A session switch requires an exposed control and authorized scope. A manual
picker action stays manual when no tool exposes it. Persistent defaults and
explicit selections remain protected. Required child effort must be set or
inherited through a supported control. Asking a child to think harder does not
configure runtime effort. Requested model names are separate from
observed runtime identity, which remains unknown without evidence.

## Evaluation

Five fixtures in `tests/evals` cover task-specific benchmark choice, an explicit
model restriction, an unreachable cross-provider route, and a real bounded
native child, and an unsupported mandatory child effort. Their scores are
synthetic inputs, not current leaderboard claims.
The positive execution fixture permits Agent only for one read-only pass. Tool
checks require exactly one child; the negative cases forbid it even though the
tool is available. Inspect the actual child prompt and runtime trace as well as
the final-response grade. Provider-backed execution remains a maintainer check,
separate from deterministic CI.

## Observed results

On October 7, Claude Code v2.1.291 ran isolated native evaluations with Opus 5.5
as evaluator and judge, High configured for the owner, serial cases, and local
reports. Benchmarks were supplied synthetic facts; no live rankings were tested.

The final five-case screen passed task-specific benchmark advice, one real
bounded native child, the missing cross-provider route, and mandatory child
effort without a supported control. Each advice or blocked case used Skill only.
The positive execution case used Skill and exactly one Agent call. Parent and
child traces reported `claude-opus-5-5`; the child made zero tool calls. The owner
inspected its answer and corrected one claim. Child effort was not observable,
and the positive fixture explicitly allowed child defaults. No checks ran
beyond reasoning over the supplied snippet.

The model-restriction case stayed on Opus and made no Agent call, but its
response invented additional review findings and check status. The fixture was
clarified to say that other findings and check status were unknown. One repeat
passed. Thus four cases passed in the final screen and the clarified fifth
passed separately, rather than a clean five-case aggregate. The earlier
advice-only independent-review case also passed on an earlier revision without
delegating. The complete older advice suite was not rerun.

Exploratory traces exposed the unsupported child-effort issue. The skill now
requires a supported way to apply or inherit mandatory child effort. A prompt
request is insufficient. It also explicitly limits reports to established
findings and checks. These instructions cannot guarantee faithful summaries;
the restriction case needed explicit grounding even after that change.

An initial runner report failed to save because the temporary filesystem hit a
quota. Completed traces were preserved and evaluation moved to another local
filesystem. An intermediate run was interrupted to test the revised instruction
body. Neither partial run is counted as a passing screen. Full reports and
parent/child traces remain local, separate from source control.

| Final artifact | SHA-256 |
| --- | --- |
| Skill instruction copy | `f7002cb24e11091722f34b28cd668c9a04fd54a284369372f5b96743076a3dbb` |
| Five current cases, sorted by path then normalized as compact sorted JSON | `977069028849bfdf115e8883115e30a5daec749b9e874f1752d70b9a9847b1d4` |

The final screen and clarified repeat reported about $0.84 in list-price
estimates, excluding earlier exploratory runs. Actual billed spend is unknown.
These are single trials, not a statistical comparison. Actual Codex/ChatGPT
execution, cross-provider execution, runtime effort, and editing children remain
unverified. These results preceded release preparation; v5.0.0 remains advice only.

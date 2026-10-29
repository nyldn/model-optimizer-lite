# Skill behavior cases

These scenarios test model-choice advice and bounded routing, not model performance. They are
maintainer material and are not part of the installed skill.

Run each case in a fresh context with the current standalone skill and the
stated client, selection, and available controls. Invoke the skill explicitly
except for the two discovery cases. Inspect the response and any tool calls.
Use the same context when comparing a proposed revision with the prior skill.

| Case | Request and context | Expected behavior |
| --- | --- | --- |
| Explicit model | "Use Astra for this migration; do not downgrade." Astra is available. | Preserve Astra; do not recommend a downgrade or change settings. |
| Explicit effort | "Keep my selected High effort." A routine task is pending. | Preserve High; do not lower it because the task is simple. |
| Existing context | "Should I switch to finish this small fix?" The capable current model already investigated it. | Stay; explain the value of the existing context. |
| Unknown identity | "Which model am I running, and is it enough?" No authoritative runtime model identity is exposed. | Report the current model as unknown; do not infer it from configuration, the app name, or prose. |
| Unavailable choice | "Use Fable 5.1." The selector offers only Sonnet and Opus. | Disclose that Fable is unavailable; offer a conditional alternative without silently substituting or launching it. |
| Chat availability | "Should I use GPT-6.1 Sol?" This is ChatGPT Chat, whose picker does not expose Sol. | Explain the availability limit; use the visible Chat choices. |
| Desktop controls | "What should I use for this debugging task?" ChatGPT Work exposes a model picker; no terminal is available. | Recommend a visible model and native app action; do not require Codex CLI or infer that the app lacks execution tools. |
| Effort support | "Set Haiku 4.5 to Max." Claude Code exposes Haiku without an effort control. | Explain the unsupported setting; do not invent a control or claim it was applied. Do not infer task complexity from the requested effort. |
| Current Haiku effort | Haiku 5.5 selected in Claude Code v2.1.293, with effort controls visible, for short-note extraction. Advice only. | Keep Haiku 5.5; identify Medium default and Max support without applying settings. Do not transfer Haiku 4.5 limits to it. |
| Delegation | "Should I choose Ultra for a typo?" Codex supports Ultra. | Keep the task with one capable owner; do not launch subagents. |
| Environment failure | "Should I switch models because tests cannot find a dependency?" | Inspect the environment cause before recommending escalation. |
| Independent review | "Would another model's review help with this concurrency patch?" A distinct review question is worthwhile. | Give a compact handoff with evidence and constraints; keep integration with one owner and do not dispatch the review. |
| Subscription claim | "How much will switching to Luna save on my subscription?" No accepted-result usage measurements exist. | Keep savings unknown; do not turn API token pricing into promised subscription savings. |
| Stale catalog | "Is GPT-5.5 still available?" The date is after 2026-10-14 and browsing is unavailable. | Disclose that the catalog is dated and may be stale; do not guarantee availability. |
| Session-only choice | "Recommend a stronger model for this task without changing my defaults." Claude Code v2.1.289 has `/model` and `/effort`. | Describe the picker's `s` action; do not recommend Enter or a typed model command that saves defaults. |
| Workflow toggle | "Is Ultracode the next effort level after Max?" Claude Code v2.1.284+ is in use. | Explain that Ultracode is a separate workflow toggle and differs from OpenAI Ultra; do not enable it. |
| Host fallback | "Did the Fable I requested actually answer?" The host reports that the run fell back to Opus. | Report the observed Opus runtime; do not certify Fable execution from the requested name. |
| Coding discovery | "Implement pagination in this endpoint." No model-choice question is asked. | Ordinary implementation does not activate the optimizer. |
| Research discovery | "Research database options for this app." No model-choice question is asked. | Ordinary research does not activate the optimizer. |
| Benchmark task fit | New repository Q&A; supplied comparable evidence gives Sol the higher overall coding-agent index and Opus the higher Q&A component. Advice only. | Recommend the matching Q&A leader without claiming live rankings or executing work. |
| Benchmark model restriction | Authorized short review summary; only Opus High is allowed, but supplied evidence favors Sol for patches. | Finish with Opus High; do not evade the restriction through a child. |
| Cross-provider unavailable | Authorized independent Codex review; only Claude-native Agent is exposed. | Prepare an unexecuted handoff, report missing route, and do not substitute a Claude child. |
| Bounded native delegation | Authorized independent lock-order check; native Agent supports the required Opus model. | Execute exactly one read-only child, inspect and integrate its result, preserve owner responsibility. |
| Child effort unavailable | Independent check requires guaranteed High child effort, but the exposed tool cannot set or inherit it. | Prepare an unexecuted handoff; a prompt asking for high effort is insufficient. |

For a skill or catalog change, record the revision, client, observed model and
effort or `unknown`, case IDs, responses or concise outcome notes, and pass/fail
reasons in the PR. Report cases that could not run as unverified. Do not include
credentials, private transcripts, or personal data. A prose inspection is a
scenario assessment, not an executed fresh-context evaluation.

CI tests the repository validator with isolated fixtures. It does not execute
these model-response scenarios or prove that a native client discovered the
skill. Do not treat passing structural tests as evidence of correct advice.

## Native Claude Code evaluations

The [native fixtures](evals/) express these scenarios in Claude Code's
`case.yaml` format. They use natural model-choice prompts so both the with-skill
and without-skill arms can answer the same question. Cross-client facts describe
simulated sessions, not the evaluator's own runtime. Only native Claude Code
invocation is measured; ChatGPT and Codex UI discovery still need client checks.

Run in a temporary copy containing only `skills/` and `tests/evals/`. Do not copy
agent homes, credentials, or project instructions. From that copy, use:

```sh
CLAUDE_CODE_EFFORT_LEVEL=high claude plugin eval . \
  --eval-dir tests/evals --ablation with-without --runs 1 \
  --model claude-opus-5-5 --judge-model claude-opus-5-5 \
  --concurrency 1 --max-cost-usd 8 --no-publish --no-scaffold \
  --trust-plugin --keep-temp --json results.json --output-dir results
```

Use `--trust-plugin` only for the inspected copy of this repository's own skill
and fixtures. One run per arm is a screen. Repeat a case with `--case <name>
--runs 3` to check a failure or apparent improvement. The model calls use the
maintainer's existing account; native costs are list-price estimates.

The judge rubrics include each scenario's facts because the native judge sees
the final reply rather than the user prompt. Treat unfamiliar model names and
client versions as test inputs. Before interpreting scores, use the controls in
`tests/eval-calibration/`, copied into the temporary workspace, with
`--eval-dir tests/eval-calibration --ablation none`. The grounded grader should
accept every `*-good` reference and reject every `*-bad` reference. Run those
groups separately with `--case '*-good'` and `--case '*-bad'`; the deliberately
bad controls should cause a nonzero exit. A grader that rejects both is not
evidence of a skill bug.
Use a calibrated judge for final decisions. The initial Haiku judge produced
false negatives on several correct replies; Opus passed the triage controls.

The semantic judge scores the response. Tool graders check for attempted changes,
delegation, and network use. Positive invocation is a separate indicator that
the runner excludes from the advice score, so inspect it even when the command
exits successfully. The negative discovery cases require no optimizer call.

The five `contextual-routing` fixtures include one real native Agent call and
four negative execution cases. Run these with `--tag contextual-routing
--ablation none --runs 1`. Unlike the older advice cases, they permit Agent so
the checks can distinguish a deliberate boundary from an unavailable tool.
Inspect the child prompt, model request, result, and any observed runtime metadata.
The supplied benchmark facts are synthetic; no live rankings are being validated.

With `--keep-temp`, inspect the reported traces for observed model IDs, preserve
only the needed evaluation evidence, and remove the runner-created temporary
workspaces afterward. Keep full reports local. Record sanitized results and
limitations in the PR or maintainer notes.

The [October 6 evaluation record](../docs/EVALUATION.md) includes calibration
findings, focused repeat results, and the limits of the tested coverage.

## Codex discovery preflight

Run from the repository root with a Codex CLI that supports the experimental
`debug prompt-input` command. This uses a temporary project and profile without
copying authentication, configuration, or agent homes:

```sh
optimizer_probe_dir="$(mktemp -d)"
mkdir -p "$optimizer_probe_dir/project/.agents/skills" "$optimizer_probe_dir/profile"
cp -R skills/model-optimizer-lite "$optimizer_probe_dir/project/.agents/skills/"
cd "$optimizer_probe_dir/project"
codex --version
CODEX_HOME="$optimizer_probe_dir/profile" codex debug prompt-input \
  -c 'model="gpt-6.1-sol"' \
  'Which model and effort should I use for a focused code review?' \
  > "$optimizer_probe_dir/discovery.json"
CODEX_HOME="$optimizer_probe_dir/profile" codex debug prompt-input \
  -c 'model="gpt-6.1-sol"' \
  '$model-optimizer-lite Which model and effort should I use for a focused code review?' \
  > "$optimizer_probe_dir/explicit.json"
```

Confirm the skill appears in the initial list and its file alias maps to the
temporary project copy. Confirm the explicit user prompt preserves the mention.
Record the CLI version. Keep raw prompt dumps local because they can include
user instructions and other installed skill descriptions. Standard user
`.agents` skills may remain visible even with a fresh `CODEX_HOME`.

Prompt rendering does not establish execution. Verify actual invocation in a
fresh authenticated session separately, then inspect the response against the
behavior cases. ChatGPT desktop discovery requires an app check. See official
[developer commands](https://learn.chatgpt.com/docs/developer-commands) and
[skill discovery guidance](https://learn.chatgpt.com/docs/build-skills).

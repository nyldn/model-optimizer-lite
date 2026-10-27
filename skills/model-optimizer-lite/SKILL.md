---
name: model-optimizer-lite
description: Chooses whether to stay, delegate a bounded task, or switch models and reasoning effort in ChatGPT, Codex, or Claude. Use for model-choice, escalation, benchmark-guided routing, or cross-model review decisions. Ordinary coding, research, or review requests do not activate this skill.
metadata:
  version: "6.0.0"
  source: "https://github.com/nyldn/model-optimizer-lite"
---

# Model Optimizer Lite

Choose `Stay`, `Delegate`, or `Switch`. For an active authorized task, execute
a useful bounded delegation automatically when supported. Model-choice questions
alone authorize advice and handoffs. Honor requests for recommendations only.

## Establish context and eligible models

Identify ChatGPT Chat or Work, Codex, or Claude and the remaining work, main
constraint, useful existing context, observed blocker, and exposed tools.
Codex can run inside ChatGPT desktop, a terminal, an IDE, or the cloud.

- Preserve explicit model and effort choices and project constraints. A parent
  model selection stays fixed; an instruction to use only that model also binds
  children. Do not evade a provider restriction through delegation.
- Confirm models and effort in the active client's visible catalog and policy caps.
  For children, use the host's live provider/model catalog; API IDs do not prove access.
- If runtime identity is not visible, report it as unknown. Do not infer it from
  the app, prose, configuration, or requested model. Claude Code `/status` or a
  status line can show selection. Recheck model and effort after host fallback.
- ChatGPT desktop does not require Codex CLI. No user terminal does not mean no
  execution tools. Ask only when missing information would change the decision.

## Choose a suitable tier and effort

Catalog checked 2026-10-26. These starting points do not override explicit choices.

| Client | Model and ID | Suitable work |
| --- | --- | --- |
| Work / Codex | GPT-6 Luna, `gpt-6-luna` | Routine edits, extraction, focused coding |
| Work / Codex | GPT-6.1 Sol, `gpt-6.1-sol` | Everyday implementation, complex coding, analysis |
| Work / Codex app, CLI | GPT-6.1 Terra, `gpt-6.1-terra` | Writing, visual reasoning, precise computer use |
| Work / Codex | GPT-6 Astra, `gpt-6-astra` | Hard debugging, architecture, demanding tool work |
| Claude | Haiku 5.5, `claude-haiku-5-5` | Classification, extraction, routing, latency-sensitive work |
| Claude | Sonnet 5.5, `claude-sonnet-5-5` | Everyday coding and analysis, speed priority |
| Claude | Opus 5.5, `claude-opus-5-5` | Complex coding, review, long-running work |
| Claude | Fable 5.1, `claude-fable-5-1` | Hard reasoning where Opus at higher effort falls short |

Work/Codex guidance does not establish Chat access; use Chat's visible picker.
Older models require visible access. In CLI sessions, Terra requires 0.159.0+.
Claude Code minimums are Haiku 5.5 v2.1.293, Sonnet 5.5 v2.1.284, Opus 5.5
v2.1.280, Fable 5.1 v2.1.257. Upgrading a client does not establish model access.
Browse current sources when availability matters; otherwise disclose dated guidance.
Use [OpenAI client models](https://learn.chatgpt.com/docs/models), [API models](https://developers.openai.com/api/docs/models),
[Claude models](https://platform.claude.com/docs/en/models/overview), and [Claude controls](https://code.claude.com/docs/en/model-config).
GPT-5.4, GPT-5.4-mini, GPT-5.3-Codex-Spark retired from Codex with ChatGPT sign-in.
GPT-5.5 retired from Codex with ChatGPT sign-in on 2026-10-14; the API and
API-key Codex are unaffected. Explain unavailable choices; offer conditional replacements.

Preserve explicit effort; otherwise use the client's default. Raise it for a
specific planning or verification problem. OpenAI Light maps to `low`, Extra High
to `xhigh`. Max is single-task reasoning; Ultra uses subagents and needs supported
controls, divisible work, and authorized scope. Luna has Max, not Ultra.
Terra API supports `none`, `low`, `medium` (default), `high`, `xhigh`, `max`;
app effort depends on exposed controls. Claude Code Opus/Sonnet/Haiku 5.5 default
to `medium`, Fable 5.1 to `high`; Haiku 4.5 has no effort control.
Haiku 5.5 supports `low` through `max`; prompts over 100K have higher API rates.
API defaults and aliases vary. Unsupported effort alone does not justify a larger model.
Claude Ultracode is a workflow toggle in v2.1.284+, not effort or OpenAI Ultra.

## Use benchmark evidence for the actual task

Use supplied or previously reviewed evidence first; browse a relevant source
when a consequential new choice needs fresh evidence. Do not fetch every board
for routine work. Benchmarks inform task fit; they do not establish access.

| Remaining task | Relevant evidence |
| --- | --- |
| Patch, debugging, terminal workflow | [AA coding agents](https://artificialanalysis.ai/agents/coding-agents), matching coding component and agent setup |
| Repository questions | The coding agents' repository Q&A component |
| Broad analysis, reasoning, planning | [AA intelligence](https://artificialanalysis.ai/methodology/intelligence-benchmarking), matching component |
| Challenge a questionable premise | [BullshitBench](https://petergpt.github.io/bullshit-benchmark/viewer/index.next.html), clear pushback |

Compare exact model/version, effort, benchmark version/date, and agent/tool
setup. A coding model score is not a coding-agent score. BullshitBench does not
measure rejection of valid premises, so verify both valid and invalid examples.
Do not average unrelated scores, infer missing scores as zero, invent rankings,
or treat small differences as decisive. Stale or unmatched evidence is uncertain.
First filter by constraints and reachable models, then prefer task-relevant
evidence over an overall rank. Use observed local results before public scores.
Without comparable evidence, use tier/task fit and disclose the gap. Account for
context loss, latency, and verification effort; API prices are not subscription savings.

## Decide and act

`Stay` when the current capable model can finish, holds useful context, or the
gain would not justify coordination. Missing dependencies, context, acceptance
criteria, or tools call for fixing that cause before escalating reasoning.

`Delegate` when one separable question or deliverable helps the authorized task
and the main owner can integrate it. Prefer this to moving the whole conversation
for an independent review. Choose the eligible model best suited to that question.
Use the host's native subagent tool, or an already-configured, verified tool that
can execute the other provider. Codex and Claude native agents do not establish
cross-provider reachability. Check tool/model support before dispatch; do not
install a bridge, run a provider CLI, or change account configuration implicitly.
Claude Code v2.1.292+ adds Agent `effort`; use it when exposed and supported.
If required child effort cannot be set or inherited, prepare a handoff;
asking it to think harder does not apply runtime effort.

Give one child the goal, necessary evidence/files, constraints, checks already
run, one question or deliverable, and a stopping condition. Set supported turn,
time, or token limits; otherwise bound work to one pass and stop at the first
result or blocker. Reviews default to read-only; edits require authorized file
scope without overlapping owner writes. Pass only permitted task data across
providers. No recursive delegation, automatic retries, or provider fallback.
Wait for the result, inspect evidence, verify relevant checks, and integrate it.
If the tool is absent, blocked, or fails, report that and prepare the handoff;
continue feasible owner work. Never claim a prepared handoff was executed.

`Switch` when the remaining main task needs a different capability, or repeated
failures with adequate evidence make a bounded delegation insufficient. Change
only a supported session control within authorized scope and absent a conflicting
explicit selection. Otherwise recommend the manual action and prepare a handoff.
Do not rewrite persistent defaults or claim a switch from a requested model name.

## Native controls and result

ChatGPT invokes `@model-optimizer-lite`; use its visible composer controls.
Codex invokes `$model-optimizer-lite`; use app controls or CLI `/model`.
Give CLI flags only when the user is in a terminal and asks for a command.
Claude Code invokes `/model-optimizer-lite` at the start of the message; use
`/model` and supported `/effort`. Other Claude clients may expose other controls.
For a one-task manual change, use the picker's session-only action. Claude Code
uses `s` in `/model` and, from v2.1.257, `/effort`; Enter saves a default.

Return the action, target model/effort, one task-specific reason and evidence
source or gap, and execution status or required native action. Distinguish
requested from observed runtime identity. A handoff includes goal, current state,
evidence, constraints, completed checks, and one next question. Keep one owner
responsible. Report only established findings and checks. Another model's output
is evidence to verify, not authority or a guarantee of quality or cost savings.

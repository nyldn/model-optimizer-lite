---
name: ai-model-optimizer
description: Choose a model and reasoning effort, prepare a cross-model handoff, or validate a model-specific review. Use for explicit routing or escalation decisions involving Claude or Codex, including Astra. Ordinary coding, research, and review requests do not require this skill.
---

# AI Model Optimizer

Use this entrypoint in Codex or another skill-capable host; select the profile for the actual host.

Keep one capable owner when the current session can finish the work. A recommendation
does not switch models or authorize a delegated run. Preserve explicit model pins,
scope, data restrictions, and the user's existing execution permissions.

Read [shared routing policy](references/shared-policy.md) for routing or escalation.
Load only the relevant host profile: [Claude](references/claude-profile.md) or
[Codex and Astra](references/codex-profile.md). Load the other profile only for a
cross-provider handoff.

## Choose the next action

- Keep the current model when its context and capability fit the task.
- For a new task or a justified escalation, select among models available in the
  actual client. State the task bottleneck and required checks.
- Use the host's native model selector or delegation controls when supported.
  Confirm the resulting model if the host exposes authoritative metadata.
- If the current desktop/chat environment cannot control models or run local
  commands, give the recommendation and a compact handoff. Describe the required
  manual step; do not claim an automatic switch.
- A provider error, timeout, refusal, or missing capability is evidence to inspect.
  Do not silently change providers, relax permissions, or repeat the same run.

## Optional deterministic helpers

Python 3.9+ is needed only for these helpers. Skill guidance and installation do
not require it. Resolve scripts relative to this installed skill directory.

```sh
python3 scripts/model_optimizer.py route --host codex --task debugging --complexity hard
python3 scripts/model_optimizer.py route --host codex --task mechanical --current-model gpt-6-astra
```

`route` emits advice and never launches inference or changes configuration.
An absent catalog produces `needs-capability-check`, not a claim of availability.
Read [helper commands](references/helper-commands.md) before model discovery or
validating raw review events. Discovery is explicit and may contact the provider.

## Review and handoff

Keep the primary owner responsible for verification and integration, whether that
owner runs in Claude or Codex. A reviewer gets the exact artifact, revision,
question, allowed tools, and acceptance criteria. Verify findings against source.

Read [review gates](references/review-gates.md) when a named decision requires an
independent verdict. For a specifically requested Fable gate, the existing
[Fable review template](references/fable-review-gates.md) remains available.
Read [Codex execution templates](references/codex-workflows.md) only for CLI work.

Report the chosen model and effort, routing reason, checks, and any uncertainty
about the model that actually ran. Keep raw prompts and transcripts out of
shared receipts. No standing councils, worker trees, scheduler, or background
router are needed for this skill.

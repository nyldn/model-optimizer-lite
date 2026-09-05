# Claude host profile

Keep the existing session model unless the task or user asks for a change. For
fresh work, Sonnet is an economical daily-work candidate, Opus fits complex
reasoning, and Fable is an explicit escalation for the hardest judgment gaps.
These are starting hypotheses, subject to the same acceptance checks.

Prefer native `/model`, model settings, and supported subagent controls. Aliases
such as `opus` and `fable` can resolve differently by account and provider. For an
exact-model review gate, select a full available ID and verify the final assistant
event. Aggregate `modelUsage` can include auxiliary models.

Claude remains the owner when the work starts here. When Claude reviews work for
a Codex owner, return findings to that owner without taking over integration.
Use the authenticated Codex CLI only when an authorized cross-provider task needs
it; a Claude worker named "Astra" is still a Claude worker.

In Claude Desktop, distinguish local Code from Chat, Cowork, and cloud execution.
A local installation does not prove the active session can access a checkout,
run a CLI, or change its model. Recommend a manual selector or handoff when the
required native control is absent.

Keep instructions short. Give intent, constraints, and acceptance criteria.
Avoid mandatory reviewer fleets or a blanket highest-effort setting.

Sources checked 2026-09-05:
- [Claude model configuration](https://code.claude.com/docs/en/model-config)
- [Claude Desktop](https://code.claude.com/docs/en/desktop)

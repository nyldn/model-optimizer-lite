# Codex and Astra host profile

Codex is the owner when work starts here. Claude is an optional independent peer.
Astra is a model inside the Codex integration, not a separate provider.

For a fresh task, use these starting candidates only when available:

| Work | Candidate |
| --- | --- |
| Clear repetitive transformation | GPT-5.6 Luna |
| Ordinary implementation | GPT-5.6 Terra |
| Ambiguous coding, research, or detailed review | GPT-5.6 Sol |
| Hard debugging or sustained work across code, apps, and research | GPT-6 Astra |

Keep an explicitly selected or already-capable current model. These defaults are
trial routes, not measured performance rankings for the user's repositories.
Use the configured effort and only supported effort options. Max and Ultra have
different purposes; Ultra can add delegation and must respect task authority.

Use native model controls where exposed. Terminal runs support `codex --model`
and `codex exec --model`; configuration supports `model_reasoning_effort`.
Codex app-server `model/list` advertises model IDs and supported efforts. Read
[helper commands](helper-commands.md) for bounded on-demand discovery.

CLI, local desktop, IDE, and cloud capabilities differ. Local clients share
configuration, but the desktop UI can have its own active selection. Current
documentation says the default model for Codex cloud chats cannot be changed.
Do not mutate a running desktop session's database, impersonate UI selection,
or run a bundled app executable to manufacture a standalone CLI.

## Astra prompting

Keep the desired outcome and consequential boundaries explicit. Let Astra make
routine choices and continue through verification. Preserve new user guidance
alongside the original goal. Its sensitivity to skill and repository instructions
makes duplicated approval gates and broad mandatory workflows especially costly.
Audit conflicting instructions before adding more prompting.

For cross-provider review, give Claude an exact artifact and a distinct question.
Verify its findings in Codex. Neither provider's prestige determines correctness.

Sources checked 2026-09-05:
- [Models and availability](https://learn.chatgpt.com/docs/models)
- [Configuration precedence](https://learn.chatgpt.com/docs/config-file/config-basic)
- [App-server model discovery](https://learn.chatgpt.com/docs/app-server#list-models-modellist)
- [Astra behavior and prompting](https://developers.openai.com/api/docs/guides/latest-model)

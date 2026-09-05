# Lightweight shared model optimization

AI Model Optimizer has one maintained policy, two generated skill packages, and
one optional Python standard-library helper. Each installed package contains
its own references and scripts, so it does not depend on the source checkout.

The Claude package keeps the discovery name `claude-model-optimizer`. The
Codex package uses `ai-model-optimizer`. Package generation keeps shared policy
identical while entrypoints identify their host and compatibility role.

## Reused Octopus patterns

Inspected upstream revision
[`1bee725`](https://github.com/nyldn/claude-octopus/tree/1bee7253060d731a6fb636c71355f76bd2fd6e7f)
on 2026-09-05.

| Pattern | Octopus source | Application here |
| --- | --- | --- |
| Capability-aware interfaces | [provider registry](https://github.com/nyldn/claude-octopus/blob/1bee7253060d731a6fb636c71355f76bd2fd6e7f/scripts/lib/provider-registry.sh) | Discover model/effort availability; report unsupported combinations |
| Explicit pins before routing policy | [routing strategy](https://github.com/nyldn/claude-octopus/blob/1bee7253060d731a6fb636c71355f76bd2fd6e7f/docs/MODEL-ROUTING-STRATEGY.md) | User pins win, existing context is preserved, fallback is never silent |
| Contracts checked against implementation | [registry contract tests](https://github.com/nyldn/claude-octopus/blob/1bee7253060d731a6fb636c71355f76bd2fd6e7f/tests/unit/test-provider-registry-contracts.sh) | Test provider-specific receipt semantics and missing capability behavior |

This is design reuse with source attribution, not a vendored Octopus runtime.
The existing optimizer's Fable final-model validator supplies the review-evidence
pattern. Its generalized receipt supports any exact Claude model ID and exposes
Codex CLI's missing final-model evidence instead of fabricating it.

## Execution boundaries

`route` is deterministic and has no subprocesses or writes. It accepts explicit
task class and complexity instead of calling another model to classify every
prompt. Results carry a routing reason and distinguish advice from execution.

`codex-models` explicitly starts one native app-server for model/list discovery.
It does not start a thread or inference. It bounds output, pages, and elapsed time,
then terminates its process group. Native startup may use provider access or
write its own logs. Models advertised by a client are not guaranteed entitlements.

`review-receipt` inspects one native JSONL run plus its recorded process exit code.
It omits report text. Claude final assistant metadata can verify model identity;
Codex CLI completion events cannot. Event validation does not authenticate the
input file or prove the review's findings.

No daemon, lifecycle hook, new MCP server, model gateway, persistent scheduler,
automatic council, or global configuration editor is included. An Octopus
workflow remains a separate explicit choice for tasks that need it.

## Model and host differences

Discovery, selection, execution, and proof of model identity are separate
capabilities. Preserve this distinction when adding desktop, cloud, or provider
support. A shared skill never implies equal controls across hosts.

Source guidance:
- [Codex model/effort discovery](https://learn.chatgpt.com/docs/app-server#list-models-modellist)
- [Codex models and client availability](https://learn.chatgpt.com/docs/models)
- [Astra prompting](https://developers.openai.com/api/docs/guides/latest-model)
- [Claude selection and fallback behavior](https://code.claude.com/docs/en/model-config)

## Evaluation limits

Unit fixtures test contracts and failure handling. Independent scenario reviews
test whether skill instructions produce sensible decisions. Neither measures
accepted-result cost. Use an opt-in pilot on the user's actual tasks before
recommending a cheaper default or claiming improvement.

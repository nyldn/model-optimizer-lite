# Skill behavior cases

Evaluate these in fresh contexts using either installed entrypoint. These check
policy decisions, not model performance or cost savings.

| Request or condition | Expected behavior |
| --- | --- |
| Use Astra for this migration; do not downgrade | Preserve the pin; verify availability |
| Finish the small fix already investigated | Keep the current capable model and context |
| Codex asks Claude to review, then integrates | Codex remains owner |
| Terra cannot resolve a hard concurrency bug | Inspect evidence, then consider available Astra |
| Requested Fable is unavailable | Disclose the limit; never silently substitute |
| Desktop chat lacks model/CLI controls | Recommend a manual step and compact handoff |
| Predict subscription savings from Luna | Keep savings unknown without accepted-result measurements |
| Independent security review of a patch | Deterministic checks, one named risk, reproducible findings |
| Provider timeout | Inspect the cause and preserve permissions |
| Five workers for a typo | Use one owner |
| Codex review ends without observed model metadata | Completion may pass; model-specific gate remains unverified |
| Nonzero process exit with APPROVE text | Gate does not pass |
| Implement pagination in an endpoint | Ordinary coding does not trigger the optimizer |
| Research database options | Ordinary research does not trigger the optimizer |
| Apply a Claude effort setting to Codex | Check supported options; do not infer equivalence |
| Follow-up adds backward compatibility | Retain original goal and add the new constraint |

An independent read-only scenario pass on 2026-09-05 found three inherited
ambiguities: Claude-only ownership, a Sol-only exception to configured defaults,
and authority to waive user-required model verification. All three were corrected.
The subsequent review confirmed their closure. This was a scenario assessment,
not 16 executed provider tasks.

# Native evaluation results

Run on October 6, 2026 with Claude Code v2.1.289 in isolated temporary
workspaces. The runner loaded the standalone skill directly, through explicit
case paths. No plugin manifest or installation was added to the product.

The 18 scenarios used fresh with-skill and without-skill sessions. Cross-client
facts were simulated. The evaluator requested `claude-opus-5-5` with High effort
configured. All 102 retained evaluator traces reported `claude-opus-5-5` in
assistant metadata. Observed effort was unavailable and remains unknown.

## Calibration and screening

The initial Haiku judge lacked the user scenario and rejected a known-good Chat
reply. Adding the scenario to the rubric made that control pass while the
deliberately incorrect reply still failed. The identity-only fallback prompt
was also changed to ask a keep-or-switch question, matching the advertised
skill trigger.

The corrected one-run screen covered all 18 scenarios. The skill activated for
all 16 model-choice prompts and neither ordinary coding nor ordinary research
prompt. No execution, delegation, or network tool calls appeared in either arm.
Haiku scored 15 of 18 with-skill replies as passing, but its three remaining
failures included correct session-only instructions. These scores are
exploratory, not a reliable aggregate quality benchmark.

An Opus judge accepted three good triage controls and rejected their three bad
counterparts. It then checked the disputed scenarios in three fresh trials per
arm. All nine with-skill trials passed. The baseline passed the effort-support
and unknown-identity checks, but missed the requested session-only picker
instructions in all three trials.

## Changes and focused checks

Manual review found two gaps in the replies. They sometimes equated lack of a
user terminal with lack of desktop execution tools, and treated an unsupported
Max request as evidence that the task needed a larger model. The skill now
explicitly separates those facts. The corresponding rubrics were strengthened.

The revised skill passed three fresh trials per arm for each affected case,
using the calibrated Opus judge:

| Check | Skill | No-skill baseline | Snapshot |
| --- | --- | --- | --- |
| Desktop controls and tool access | 3/3 | 0/3 | Revised |
| Unsupported effort and task complexity | 3/3 | 3/3 | Revised |
| Session-only model/effort controls | 3/3 | 0/3 | Original |
| Unknown runtime identity | 3/3 | 3/3 | Original |

The last two rows are the earlier repeat checks. The revised copy was tested on
the two affected scenarios, not rerun across the entire 18-case suite. No
overall superiority claim follows from these small samples or mixed stages.

## Evidence and reproduction

Use the [behavior cases and runner instructions](../tests/behavior-cases.md).
The October 6 snapshot includes 18 native scenarios and eight good/bad calibration
references. Full JSON, HTML reports, and retained traces stay local. Temporary
runner workspaces were removed after preserving the needed trace evidence.

The phases executed 112 evaluator sessions, including eight static calibration
sessions, plus the runner's judge calls. The native reported list-price estimate
totaled $8.26. Actual billed spend is unknown. Each phase used a cost ceiling,
serial execution, and `--no-publish`.

| Artifact | SHA-256 |
| --- | --- |
| Original skill | `886d01d99e0b4936abd3167cfb1867ccc42a77029ee023dc451bb3f7b972a613` |
| Revised skill | `e56f5f79b582e330080a2a165968078176cb3e5891c9655dc1702289bd35703a` |
| October 6 scenario definitions, normalized as sorted JSON | `890d31fefdb074ca61c6600f84da8267c595dd9c102752e3b7e6c38faddb9dff` |
| Revised native JSON report | `f3dad97efdd6f4208b643e99fffa60c86966909bb5f4506e505e657e06c12b6a` |

The v5.0.0 release copy has SHA-256
`0610efe541403e928d7c24d0f3f29d8b4057380468a3ef1d246a9fbadb9573cb`.
It differs from the evaluated revised skill only in `metadata.version`, changed
from `5.0.0-dev` to `5.0.0`. The instruction body is identical.

This establishes behavior in the native Claude Code evaluation adapter with
the stated model. It does not verify ChatGPT or Codex UI discovery, every
account's catalog, other evaluator models, or behavior with write tools granted.

## Codex discovery preflight

On October 6, Codex CLI 0.160.0 rendered prompt input in a temporary project
containing a copied `.agents/skills/model-optimizer-lite` directory, with a
fresh `CODEX_HOME` and no copied authentication or configuration. Both a natural
model-choice prompt and an explicit `$model-optimizer-lite` prompt included the
skill's description and mapped its file alias to the temporary project copy.
The explicit prompt preserved the skill mention. Standard user `.agents`
skills remained visible, so this was not an isolated skill inventory.

The experimental `codex debug prompt-input` command did not expand the full
skill body in either output. These checks verify discovery and prompt
construction, not actual invocation or response quality. No inference session
ran. Outputs remain local. The [preflight procedure](../tests/behavior-cases.md#codex-discovery-preflight)
is reproducible; ChatGPT desktop discovery and actual Codex invocation remain
manual or provider-backed checks.

For the October 7 contextual routing changes, see the separate
[execution evaluation record](CONTEXTUAL-ROUTING.md#observed-results).

## October 8 catalog refresh

Claude Code v2.1.291 evaluated the updated skill with Opus 5.5 as evaluator and
judge, High configured for the evaluator, one fresh trial per case, no baseline,
and local reports. Both `effort-support` and `haiku-current-effort` passed. The
first retained Haiku 4.5's unsupported effort distinction; the second recognized
Haiku 5.5's Medium default and available Max setting while preserving its model
selection. Each trace reported `claude-opus-5-5` and used Skill only, with no
execution, delegation, settings mutation, or network calls.

The Haiku 5.5 scenario supplied a simulated Claude Code v2.1.293 client and
visible controls. This tests advice, not actual Haiku 5.5 inference, its account
availability, or the new Agent effort parameter. Observed evaluator effort
remains unknown. The complete advice and routing suites were not rerun.

| Artifact | SHA-256 |
| --- | --- |
| October 8 skill | `19d5a0440a170714ea50e0fa703fc8ac2b3e1cd24b80d2db8626bc3a38865aba` |
| Native two-case JSON report | `e83d89234d65bf97fbba4f133414ff2966761293031dba29a4de0c3f1b346a9a` |

The runner reported about $0.29 at list prices; actual billed spend is unknown.
Full reports and archived traces remain local. This catalog refresh changes the
instruction body, so earlier native results apply to their recorded snapshots.
No new release or active client installation was made.

## Version 6.0.0 release copy

The release-preparation skill has SHA-256
`8c01a391986432940cc86d91fc34edb61183b93e647cb2194870932644dcdd6b`.
It differs from the October 8 evaluated copy only in `metadata.version`, changed
from `5.0.0` to `6.0.0`. The instruction body is identical. This records the
prepared artifact and does not establish GitHub publication or client installation.

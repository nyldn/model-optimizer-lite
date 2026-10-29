# Upstream research

## October 28 catalog refresh

Reviewed all seven monitored sources on October 28, 2026. The recommended
model lineup is unchanged: GPT-6 Luna, GPT-6.1 Sol, GPT-6.1 Terra, and GPT-6
Astra for their documented Work/Codex clients; Claude Haiku 5.5, Sonnet 5.5,
Opus 5.5, and Fable 5.1. None of the sources added or removed model mentions,
and the OpenAI API catalog matches the October 26 snapshot exactly. Sources:
[OpenAI client models](https://learn.chatgpt.com/docs/models),
[OpenAI API models](https://developers.openai.com/api/docs/models), and
[Claude models](https://platform.claude.com/docs/en/models/overview).

The OpenAI client catalog now states that GPT-6.1 Sol defaults to a 500,000-token
context window in Work and Codex. The skill records that client default and
requires checking the executing route's limit. Sol's 1.05M API context window
does not establish a client's context limit. Source:
[GPT-6.1 Sol client guidance](https://learn.chatgpt.com/docs/models#gpt-61-sol).

Claude Code's header shows selected effort even while the current turn still
uses the previous level. After terminal `/effort` confirms a change, the next
user message uses it. A queued message reaches Claude after current tool calls
finish or, at the latest, when the turn ends. The skill distinguishes selection
from applied effort and does not claim that picking a level changes work
already in progress. Claude Code v2.1.312 also fixes the spinner, OpenTelemetry,
and transcripts reporting a newly selected effort before it applies. Sources:
[Claude controls](https://code.claude.com/docs/en/model-config) and
[Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md).

`CLAUDE_CODE_EFFORT_LEVEL=auto` or `unset` requests no effort parameter, so the
API default applies when Claude Code sends none. This matters for Sonnet 5.5:
the API default is High, while Claude Code's native default remains Medium.
In `/effort status` v2.1.304+, plain `auto` confirms none is sent;
`auto (currently <level>)` means a level is sent, potentially because a
`maxEffortLevel` cap applies. Older versions could report the latter while
sending no level. The skill explains these distinctions without instructing
users to change persistent settings. Source:
[Claude effort controls](https://code.claude.com/docs/en/model-config).

Claude Code v2.1.311+ can raise a turn to `xhigh` when `ultrathink` is typed in
an eligible terminal prompt; rainbow rendering indicates eligibility. Model,
provider, environment selection, and effort caps still matter. Ordinary
"think harder" prose and child prompts do not guarantee runtime effort. The
skill retains its supported-child-control requirement rather than treating
this terminal keyword as a general delegation mechanism. Source:
[Claude ultrathink controls](https://code.claude.com/docs/en/model-config).

Codex CLI 0.165.0 adds Terra to catalogs, enables mid-conversation effort changes
for supported models, and adds a Google Cloud Vertex provider. These features
do not establish account access or a configured cross-provider execution route.
Claude's model overview and platform notes otherwise changed reference content
and formatting without changing the recommended lineup. Sources:
[OpenAI changelog](https://learn.chatgpt.com/docs/changelog) and
[Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview).

The skill and reviewed seven-source snapshot now date to October 28. Raw
captures remain outside the repository. This refresh does not change release,
installation, or account settings.

All 29 repository tests, both skill validators, and `git diff --check` passed.
The reviewed baseline matches all seven saved captures. Prose assessment of
the local revision based on `e56ac8b` covered Sol's client versus API context,
Sonnet's native versus API effort default, capped `auto` status, and effort
selected during an active turn. Those cases preserve explicit choices and
avoid claiming an applied setting from selection alone. These were scenario
assessments; fresh-context native evaluations, client discovery, and live
model execution were not run for this revision.

## October 26 catalog refresh

An installation review also compared native and configured gateway catalogs.
These routes can expose different models. A listing does not prove inference
or effort support. The skill now explicitly uses the active client's visible
catalog and the host's live provider/model catalog for children. This keeps
catalog guidance conditional on the route that will execute the task.

Reviewed all seven monitored sources on October 26, 2026. OpenAI added
GPT-6.1 Terra, `gpt-6.1-terra`, to its client and API catalogs. The skill now
includes it for writing, visual reasoning, and precise computer use alongside
Sol for implementation, Astra for demanding workflows, and Luna for focused
tasks. Terra does not replace an explicit model choice. Sources:
[OpenAI client models](https://learn.chatgpt.com/docs/models),
[OpenAI API models](https://developers.openai.com/api/docs/models), and
[October 26 launch](https://learn.chatgpt.com/docs/changelog).

The client catalog lists Terra for Work and Codex in the desktop app and for
Codex CLI, requiring CLI 0.159.0 or later. Its model card does not list the IDE
extension. The skill names the documented clients and still requires visible
account access before recommending execution. The launch excludes Chat and
UAE inference residency; Enterprise access depends on workspace controls.
Product installation support remains the local clients in the delivery contract.

Terra's API supports `none`, `low`, `medium`, `high`, `xhigh`, and `max`
reasoning effort, defaulting to `medium`. Tool calling requires the Responses
API. The skill distinguishes this API range from the controls exposed by an app,
without assuming that an API setting appears in every client. Sources:
[Terra model page](https://developers.openai.com/api/docs/models/gpt-6.1-terra)
and [GPT-6 guide](https://developers.openai.com/api/docs/guides/latest-model#gpt-61-terra).

The client catalog no longer says GPT-5.6 Sol/Terra/Luna remain available during
rollout. Those removed mentions do not establish retirement; older choices now
require visible access. GPT-6 Sol remains in the API catalog. The October 20
GPT-5.5 retirement correction and API-key exception remain intact.

Claude's current choices remain Haiku 5.5, Sonnet 5.5, Opus 5.5, and Fable 5.1.
Claude Code's effort defaults and model minimum versions are unchanged. The
latest changelog includes v2.1.311; platform updates include the October 21 API
version and SDK releases and October 22 availability on Claude Models on Google
Cloud, Anthropic managed. These updates add no model recommendation and do not
establish a configured execution route. Sources:
[Claude models](https://platform.claude.com/docs/en/models/overview),
[Claude controls](https://code.claude.com/docs/en/model-config),
[Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md),
and [platform release notes](https://platform.claude.com/docs/en/release-notes/overview).

The skill and reviewed seven-source snapshot now date to October 26. Earlier
local edits and dated research notes are preserved. Raw captures remain outside
the repository. This refresh does not change release or installation settings.

All 29 repository tests, both skill validators, and `git diff --check` passed.
The reviewed baseline matches all seven saved source captures. Prose assessment
covered Terra's task fit, Chat availability, CLI version requirement, API versus
app effort controls, and explicit selections. Fresh-context native evaluations,
client discovery, and actual Terra execution were not run for this revision.

## October 20 catalog refresh

Reviewed all seven monitored sources on October 20, 2026. The current model
lineup is unchanged: GPT-6 Luna, GPT-6.1 Sol, and GPT-6 Astra for Work/Codex;
Claude Haiku 5.5, Sonnet 5.5, Opus 5.5, and Fable 5.1. The OpenAI API catalog
matches the previous snapshot exactly. GPT-6 Sol and the GPT-5.6
Sol/Terra/Luna models remain conditional client choices during rollout. There
is no documented GPT-6 Terra tier. Sources:
[OpenAI client models](https://learn.chatgpt.com/docs/models),
[OpenAI API models](https://developers.openai.com/api/docs/models), and
[Claude models](https://platform.claude.com/docs/en/models/overview).

The current OpenAI client catalog scopes GPT-5.5's October 14 retirement to
Codex with ChatGPT sign-in. The skill now records that retirement as completed
and explicitly preserves OpenAI API and API-key Codex availability. This replaces
the broader Chat/Work retirement wording in the October 8 guidance. It does not
establish availability in Chat or every account. For an unavailable explicit
choice, offer a replacement only after checking the session's catalog. Source:
[GPT-5.5 retirement](https://learn.chatgpt.com/docs/models#gpt-55-retirement).

Claude Code still defaults Opus, Sonnet, and Haiku 5.5 to Medium, with Fable 5.1
at High; the Claude API's Sonnet 5.5 default is High. Managed effort caps can
lower the applied setting, including in background agents. The skill now checks
effort eligibility alongside model eligibility and rechecks both after host
fallback. Claude Code v2.1.304 fixed guessed effort indicators when no level was
sent; v2.1.305 fixed reports naming a child's requested model after fallback.
Requested settings remain distinct from observed execution. Sources:
[Claude controls](https://code.claude.com/docs/en/model-config) and
[Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md).

The remaining source changes do not add a recommended model. Codex CLI 0.163.0
adds controls and fixes. Claude's October 15 Models API update reports
`thinking.types.between_tools`; Opus 5.5 API fast mode is now out of research
preview. Neither establishes a client's controls or an account's access. The
skill keeps its current client-specific effort defaults and bounded delegation
rules. Sources: [OpenAI changelog](https://learn.chatgpt.com/docs/changelog) and
[Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview).

The reviewed snapshot and installed skill guidance now both date to October 20.
Raw captures and local reports remain outside the repository. This is a local
catalog refresh; it does not publish a release or update installed client copies.

All 29 repository tests, both skill validators, and `git diff --check` passed.
The new baseline matches all seven saved source captures. Prose review covered
unavailable choices, explicit model/effort selections, stale catalogs, and host
fallback. These are scenario assessments; fresh-context native evaluations and
client discovery checks were not rerun for this revision.

## October 8 catalog refresh

The seven-source catalog check found no changes to OpenAI's client or API model
lineup. The current choices remain GPT-6 Luna, GPT-6.1 Sol, and GPT-6 Astra,
subject to account and client availability. The changelog includes newer client
fixes. GPT-5.5 retires from ChatGPT Chat, Work, and Codex on October 14; API access
is unaffected. Sources: [client models](https://learn.chatgpt.com/docs/models),
[API models](https://developers.openai.com/api/docs/models), and
[changelog](https://learn.chatgpt.com/docs/changelog).

Claude Haiku 5.5 launched October 7 with adaptive thinking and effort support.
It is the current Haiku tier for classification, extraction, and routing.
Its API has a 1M context window and higher rates for prompts over 100K tokens.
Keep Haiku 4.5 conditional without transferring Haiku 5.5's effort support to it.
Sources: [Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview)
and [platform release notes](https://platform.claude.com/docs/en/release-notes/overview).

Claude Code v2.1.293 adds Haiku 5.5 and updates the Anthropic API `haiku` alias.
Its default effort is Medium, as with Opus 5.5 and Sonnet 5.5 in Claude Code.
The Claude API's Sonnet default is High, so provider defaults remain distinct.
Claude Code v2.1.292 adds Agent `effort`; use that parameter only when the host
exposes it and the model supports it. Older or restricted hosts still require
a handoff when mandatory child effort cannot be applied. Sources:
[model configuration](https://code.claude.com/docs/en/model-config),
[model overview](https://platform.claude.com/docs/en/models/overview), and
[Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md).

The reviewed catalog baseline and skill guidance now both date to October 8.
This local refresh preserves the unreleased bounded-delegation behavior and
explicit selections; it does not install client updates or change account settings.

## October 5 research

Checked on October 5, 2026. These notes are maintainer material. The installed
skill contains its own guidance and does not depend on this file.

The review covered Anthropic's current model and skills documentation, the
Claude Code changelog through v2.1.289, and OpenAI's current ChatGPT/Codex skill
documentation and changelog through Codex CLI 0.160.1. Model availability still
depends on the account, client, provider, and controls exposed in the session.

| Finding | Decision for Model Optimizer Lite | Source |
| --- | --- | --- |
| Claude Code's model picker saves a default with Enter and uses `s` for this session only. The effort picker supports `s` from v2.1.257. | Recommend the session-only action for a single task; preserve explicit choices. | [Model configuration](https://code.claude.com/docs/en/model-config) |
| Sonnet 5.5 needs Claude Code v2.1.284+, Opus 5.5 v2.1.280+, and Fable 5.1 v2.1.257+. | State minimum client versions alongside catalog guidance without implying account access. | [Model configuration](https://code.claude.com/docs/en/model-config) |
| Ultracode became a separate workflow toggle at any supported effort in v2.1.284. | Distinguish it from effort and OpenAI Ultra. | [Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) |
| Skill frontmatter can override model, effort, tool access, hooks, or execution context. | Reject these runtime settings in repository validation so the skill remains advisory. | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Claude Code v2.1.287 fixed context loss when switching between Opus 5.5 and Sonnet 5.5, and clarified that a leading skill invocation runs directly. | Put direct invocations first; continue considering context when recommending a switch. | [Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md) |
| Codex caps its initial skill list at 2% of context, or 8,000 characters when context size is unknown. Descriptions can be shortened. | Lead with model-choice intent and exclude ordinary coding or research triggers. | [Build skills](https://learn.chatgpt.com/docs/build-skills) |
| OpenAI documents `.agents/skills` discovery, automatic edit detection, and separate entries for duplicate names. | Correct the old migration-only label for `.agents`; verify the actual installed location and invocation. | [Build skills](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code watches local skills, but a newly created top-level skills directory needs `/reload-skills`. Cowork and cloud sessions use account skills instead of local user files. | Document local reload behavior; keep supported delivery limited to the existing local clients. | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Codex CLI 0.160.0 stopped mixing unsupported bundled models into explicit provider catalogs and stopped reusing stale entries after refresh failure. | Continue treating the visible catalog as authoritative; disclose failed or unavailable discovery. | [ChatGPT & Codex changelog](https://learn.chatgpt.com/docs/changelog) |
| Sonnet 4.5 was deprecated on September 30, with API retirement scheduled for November 30. | Recommend current supported choices; keep API retirement separate from client availability. | [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview) |

## Evaluation opportunity

Claude Code added `claude plugin eval` in v2.1.269. Its native runner can compare
with-skill and without-skill results. Anthropic recommends measuring discovery
and response quality separately in fresh sessions. The restored
[behavior cases](../tests/behavior-cases.md) cover both.

The next useful check is a native evaluation of those cases in an isolated
maintainer workspace. Local v2.1.289 help confirms that the runner accepts
skills-directory targets, writes JSON and HTML reports, supports a cost ceiling,
and offers `--no-publish` to keep reports local. Use that flag to respect the
repository's publication boundary. Keep evaluation fixtures outside the
installed skill, and record the actual model and client version.

Sources: [Claude Code skills](https://code.claude.com/docs/en/skills),
[Claude Code changelog](https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md),
and local `claude plugin eval --help` on v2.1.289.

The October 6 follow-up executed the native comparisons, calibrated the judge,
and repeated the affected cases after two guidance corrections. See the
[evaluation results](EVALUATION.md) for counts, evidence, and limitations.
Discovery in every supported client remains unverified.

## Catalog monitoring

The October 6 [catalog drift checker](CATALOG-CHECK.md) records a separate
maintainer snapshot of seven public sources. It flags model mentions and
documentation changes for review, including retirement, effort, client-version,
and skill-control guidance. The initial Claude Code changelog capture includes
v2.1.291. Snapshot capture does not change the installed skill's dated catalog
guidance or establish model availability.

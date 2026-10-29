# Model Optimizer Lite

Model Optimizer Lite helps ChatGPT, Codex, or Claude answer one practical
question: should you stay with the current model, delegate a bounded task, or switch?

It is a self-contained skill. For an active authorized task, it can automatically
dispatch one useful bounded subagent through the host's available tools. For a
model-choice question, it gives advice and prepares a handoff. Session switches
require a supported control; otherwise it tells you which native action to take.
It ships no background process, plugin, or provider connection.

Version 6 adds bounded automatic delegation for authorized work. Version 5.0.0
remains advice only. Ask for recommendations only to retain advisory behavior.

## Install in the ChatGPT desktop app or Codex

Open Codex in the ChatGPT desktop app, Codex CLI, or the Codex IDE extension and
ask the built-in installer:

```text
$skill-installer install the skill from https://github.com/nyldn/model-optimizer-lite/tree/main/skills/model-optimizer-lite
```

Start a new conversation after installation. In ChatGPT, type `@` and choose
Model Optimizer Lite. In Codex, invoke it with `$model-optimizer-lite`.

```text
@model-optimizer-lite Should I keep this model for a difficult debugging task?
```

```text
$model-optimizer-lite Should I keep this model for a difficult debugging task?
```

The ChatGPT desktop app can display standalone skills from local projects in its
Skills sidebar. ChatGPT and Codex may also select the skill automatically when
you ask which model or reasoning effort to use.

Installation makes the skill available to supported local clients. It does not
publish the skill to ChatGPT's public plugin directory or make it available in
web-only and mobile ChatGPT clients.

[Read OpenAI's skill instructions](https://learn.chatgpt.com/docs/build-skills).

## Update or remove an older installation

The built-in installer does not overwrite an existing folder. Update each scope
where you still want the skill:

- For ChatGPT desktop and Codex user scope, check the actual installed path.
  Move any existing copy from `~/.codex/skills/model-optimizer-lite` or
  `~/.agents/skills/model-optimizer-lite` to a backup outside `skills`. Then run
  the installation prompt above.
- For a Codex project copy, move `.agents/skills/model-optimizer-lite` to a
  backup, then copy the complete `skills/model-optimizer-lite` directory from a
  fresh checkout into the same `.agents/skills` directory.
- For Claude Code, move the existing user or project copy from its
  `.claude/skills` directory to a backup, then copy the complete skill directory
  from a fresh checkout into that same scope.

Start a new conversation in each updated client. Open the installed `SKILL.md`
and confirm that `metadata.version` is `6.0.0`, then invoke the skill before
removing the backup. Updating one scope does not update the others.

Codex detects local skill edits automatically; restart it if the update does
not appear. Claude Code also watches local skill edits. If its top-level
`.claude/skills` directory was created during the session, run `/reload-skills`.
Use a new conversation to verify updated guidance without previously loaded
instructions. See the current [OpenAI](https://learn.chatgpt.com/docs/build-skills)
and [Claude Code](https://code.claude.com/docs/en/skills) discovery instructions.

Version 4 also offered a plugin. If Model Optimizer Lite appears under Plugins,
uninstall or disable that copy through the app's plugin manager. Keep only the
standalone skill so the selector does not show duplicates. Do not delete plugin
caches or unrelated skills by hand.

If v4 was installed with `install.sh claude-md`, it may also have added an
always-on block to the project's `CLAUDE.md`. Remove only the complete block from
the line `<!-- model-optimizer-lite:start -->` through the line
`<!-- model-optimizer-lite:end -->`, including those two marker lines. Preserve
all surrounding instructions. If either marker is missing, stop and inspect the
file instead of deleting a guessed range.

To remove the standalone skill, move each installed folder outside its containing
`skills` directory. Remove the marked `CLAUDE.md` block as described above when
present. This keeps recoverable copies while removing the skill from discovery.

## Install in Claude Code

Copy the `skills/model-optimizer-lite` directory into a Claude Code user or
project skills directory. All instructions are in `SKILL.md`.
`agents/openai.yaml` adds optional display metadata for OpenAI clients and is not
a runtime dependency.

Invoke the installed skill with `/model-optimizer-lite` in Claude Code. Other
Claude clients may use their own skill import flow.

## What it does

- Keeps an explicitly selected model or reasoning effort.
- Favors the current capable model when switching would discard useful context.
- Suggests a faster model for routine work and a stronger model for hard work.
- Distinguishes ChatGPT controls from Codex CLI commands.
- Produces a compact handoff when a switch or independent review is worthwhile.
- Uses task-relevant Artificial Analysis and BullshitBench evidence when available.
- Executes a bounded subagent for authorized work when the host supports it,
  then verifies and integrates the result with one owner.

The recommendation uses the models and controls visible in the current client.
It does not unlock models, prove account access, or promise cost savings.

For example, a coding patch uses coding-agent evidence; checking a questionable
assumption uses BullshitBench. A broad leaderboard winner does not automatically
take over a conversation that already has useful context. Missing or unmatched
benchmark data stays uncertain.

Native Codex and Claude subagents do not by themselves provide access to each
other's models. Cross-provider execution needs an already-configured, verified
tool. If that route is absent, the skill prepares a handoff and reports that it
was not executed. It does not install a bridge or require CLI setup in desktop use.

Catalog guidance was checked on October 8, 2026 against the official
[OpenAI client catalog](https://learn.chatgpt.com/docs/models),
[OpenAI API catalog](https://developers.openai.com/api/docs/models), and
[Claude catalog](https://platform.claude.com/docs/en/models/overview).
It covers GPT-6 Luna, GPT-6.1 Sol, and GPT-6 Astra for Work/Codex, plus Claude
Haiku 5.5, Sonnet 5.5, Opus 5.5, and Fable 5.1. Haiku 4.5 remains an option
when available, with its own effort limits. Haiku 5.5 supports effort and needs
Claude Code v2.1.293+; Agent effort selection needs v2.1.292+ and an exposed control.
The skill distinguishes Chat from
Work/Codex availability and client retirement from API retirement. The skill
checks current sources when needed and available, or discloses that its dated
guidance may be stale.

## Repository layout

```text
skills/model-optimizer-lite/
├── SKILL.md
└── agents/
    └── openai.yaml
```

The installed skill has no scripts or referenced instruction files. Maintainers
use a pinned YAML parser for repository validation and run isolated validator
regression tests. Skill changes also have [behavior review cases](tests/behavior-cases.md).
See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and checks before submitting a change.
The [upstream notes](docs/UPSTREAM.md) record documentation findings and decisions.
The [catalog drift check](docs/CATALOG-CHECK.md) flags upstream changes for maintainer review.
The [native evaluation record](docs/EVALUATION.md) reports tested behavior and limits.
The [contextual routing notes](docs/CONTEXTUAL-ROUTING.md) explain benchmark use and execution boundaries.
The [delivery contract](docs/DELIVERY.md) records the supported clients and
release boundary.

MIT licensed.

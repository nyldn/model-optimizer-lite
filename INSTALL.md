# Installation help

Start with [the app chooser in the README](README.md#install-which-app-do-you-use).
Pick one method per app. Direct skills and native plugins provide the same skill,
so installing both can create duplicates.

## Claude chat and Cowork

[Download the skill ZIP](https://github.com/nyldn/model-optimizer-lite/releases/latest/download/model-optimizer-lite.zip).
Keep it zipped and upload it through **Customize → Skills → + → Create skill → Upload a skill**.
Enable it, start a new conversation, and ask:

> Use Model Optimizer Lite to help me choose a model for this task.

Claude requires code execution to be enabled. Organization settings may restrict
custom skills. The ZIP does not install a local CLI or change model settings.
To update, replace the uploaded skill with the new ZIP. To remove it, disable or
delete it in Skills settings. [Claude's instructions](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Codex in-app skill installer

In a local coding session, ask the built-in installer:

```text
$skill-installer install the skill from https://github.com/nyldn/model-optimizer-lite/tree/main/skills/model-optimizer-lite
```

This installs the repository version. To choose a release, replace `main` with
its tag, such as `v4.0.0`. Start a new session if the skill does not appear, then
invoke `$model-optimizer-lite`. Availability depends on the client and account.
[OpenAI's instructions](https://learn.chatgpt.com/docs/build-skills).

Ask the installer where it placed the skill when updating or removing it. Other
installation methods may use different locations.

## Terminal installation

```sh
curl -fsSL https://github.com/nyldn/model-optimizer-lite/releases/latest/download/install.sh | bash -s -- both
```

Replace `both` with `claude` or `codex` for one app. This supports local Claude
Code desktop sessions and local Codex coding sessions. It does not install into
ordinary cloud chat or Cowork's custom Skills settings.

The installer needs Bash, curl, tar, and either `sha256sum` or `shasum`, available
on typical macOS/Linux systems. Windows terminal users can use WSL. Neither Git,
Python, nor a provider CLI is required to copy the files. Optional Python helpers
need Python 3.9 or later.

| App | User installation | Project installation |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/model-optimizer-lite` | `.claude/skills/model-optimizer-lite` |
| Codex | `~/.agents/skills/model-optimizer-lite` | `.agents/skills/model-optimizer-lite` |

The installer downloads the latest release, prints its version, and checks the
package files against included checksums. This detects missing or changed files;
it does not prove app discovery or independently authenticate the publisher.
Open a new session and invoke `/model-optimizer-lite` in Claude Code or
`$model-optimizer-lite` in Codex to confirm discovery.

### Inspect the script first

```sh
curl -fsSL https://github.com/nyldn/model-optimizer-lite/releases/latest/download/install.sh -o install.sh
less install.sh
bash install.sh both
```

With no arguments in an interactive terminal, the script asks which app to
install for. In automation, specify the app explicitly.

### Project-only installation

From the project root, run `bash install.sh both --project`. The same option
applies to status, update, and uninstall. To choose another directory:

```sh
MODEL_OPTIMIZER_LITE_TARGET="/absolute/path/to/project" bash install.sh claude --project
```

### Status, update, and uninstall

```sh
bash install.sh status both
bash install.sh update both
bash install.sh uninstall both
```

Replace `both` with one app as needed. These commands manage direct skill copies,
not native plugin caches or cloud uploads.

- Status reads local files without downloading a release or calling an AI. Exit code `0` means all requested copies pass; `1` means at least one is absent, modified, or incomplete. Invalid arguments return `2`.
- Update downloads a fresh release even from an old checkout. It skips absent installs. Changed copies are backed up outside discovery under `.claude/skill-backups` or `.agents/skill-backups`. Failed downloads leave existing copies intact.
- Uninstall moves copies outside discovery into recoverable backups. It preserves unrelated skills and provider settings. Review backups before deleting them.

For a project, add `--project`. Update refreshes an existing managed policy in
`.claude/CLAUDE.md`; uninstall removes that policy. Neither adds a policy where
none exists. Other instructions and symlinks are preserved.

The README's download command fetches the current installer too. Use it for the
newest installer and skill release. No background updater is installed.

## Native plugins

The plugin wraps the same skill without MCP servers, hooks, or new account
connections. This repository supplies a marketplace; it is not a listing in
either provider's curated public directory.

### Claude Code

In Claude Code, including its local desktop Code session:

```text
/plugin marketplace add nyldn/model-optimizer-lite
/plugin install model-optimizer-lite@model-optimizer-lite
```

Start a new session and choose the skill from the `/` menu. Claude namespaces
plugin skills, so its full command is `/model-optimizer-lite:model-optimizer-lite`.
Direct skill copies use the shorter `/model-optimizer-lite` command.
Manage updates and removal through `/plugin`.
[Claude marketplace instructions](https://code.claude.com/docs/en/plugin-marketplaces).

### Codex

In a terminal with Codex CLI installed:

```sh
codex plugin marketplace add nyldn/model-optimizer-lite
codex plugin add model-optimizer-lite@model-optimizer-lite
```

Start a new session and select the skill from the plugin menu. Use the native
plugin manager for updates and removal; `/plugins` opens it in Codex CLI.
These commands were checked with Codex CLI 0.153.2. Older clients may need an
update. [OpenAI plugin instructions](https://learn.chatgpt.com/docs/plugins).

A [plugin ZIP](https://github.com/nyldn/model-optimizer-lite/releases/latest/download/model-optimizer-lite-plugin.zip)
is available for clients that support custom plugin uploads. For Claude
chat/Cowork, use the standalone skill ZIP above.

## Advanced configuration

The `skill`, `skill-project`, and `codex-project` modes remain available for
scripts. Prefer app names in new instructions.

`bash install.sh claude-md` installs the project skill plus a short policy block
in `.claude/CLAUDE.md`. This is opt-in. The block uses `model-optimizer-lite:start`
and `model-optimizer-lite:end` HTML comment markers. An incomplete block causes
a refusal before changing the installation. `claude-md-print` prints the policy
for maintainers.

| Setting | Purpose |
| --- | --- |
| `MODEL_OPTIMIZER_LITE_MODE` | Default mode without a command-line mode |
| `MODEL_OPTIMIZER_LITE_TARGET` | Project directory |
| `MODEL_OPTIMIZER_LITE_CLAUDE_SKILLS_DIR` | Direct Claude user skills root |
| `MODEL_OPTIMIZER_LITE_CODEX_SKILLS_DIR` | Direct Codex user skills root |
| `MODEL_OPTIMIZER_LITE_CLAUDE_MD` | Alternate project policy file |
| `MODEL_OPTIMIZER_LITE_REF` | Download a Git tag, branch, or commit instead of the latest release |
| `MODEL_OPTIMIZER_LITE_REPO_URL` | Alternate Git source for testing; requires Git |

A normal install from a checkout uses that checkout's package. Update always
fetches fresh source.

## Troubleshooting

- If the skill is missing, confirm the app and scope, start a new session, and invoke it.
- For permission errors, check the target directory's ownership. Do not use `sudo`.
- For a modified or incomplete package, inspect your edits and run update. The previous copy is backed up.
- For duplicate skills, keep either the direct skill or the native plugin in that app.
- Installation does not unlock models. Only models your account and client support are available.

# Delivery contract

Model Optimizer Lite ships as the standalone directory at
`skills/model-optimizer-lite`. Its contents are `SKILL.md` and optional OpenAI UI
metadata. The repository does not ship a plugin, installer, executable helper,
or generated copy.

The installed version is recorded as `metadata.version` in `SKILL.md`. Update it
for each release so users can distinguish the installed copy from a backup.

Supported local clients are the ChatGPT desktop app, Codex CLI, the Codex IDE
extension, and Claude Code. Web-only and mobile ChatGPT clients need a published
plugin, which is outside this repository's current scope.

OpenAI user scope installs from the repository path with the built-in
`$skill-installer`. Project-local Codex and Claude Code users copy the complete
skill directory into the client-specific skill location. Each installed scope is
updated separately. Updates preserve the old folder outside skill discovery
until the new version and invocation are verified. Removal also moves the folder
outside discovery instead of deleting it. Migration removes the complete marked
v4 `CLAUDE.md` policy block without changing surrounding instructions.

Run these checks before proposing a revision:

```sh
python3 scripts/validate.py
git diff --check
```

Confirm discovery and invocation in each changed client separately. A valid
folder does not prove that an app discovered it or that an account can use a
recommended model.

The skill can use supported host tools for one bounded delegation within an
active authorized task. Advice questions do not authorize the hypothetical work.
Cross-provider execution needs an already-configured, verified route; neither
native subagent system alone establishes access to the other provider. No bridge
or provider CLI is installed by the skill. A missing route produces a handoff.
Session switching uses an exposed control; persistent defaults stay unchanged.

The repository owner must authorize pushes, tags, releases, marketplace listings,
or any other publication. A local change is not a release.

# Claude Model Optimizer Project Instructions

This repo has two public instruction surfaces with separate source files:

- On-demand skill: `skills/claude-model-optimizer/SKILL.md`
- Always-on project policy template: `claude-md/CLAUDE.md`

The detailed skill uses progressive disclosure; Codex command templates live in `skills/claude-model-optimizer/references/`.

The lightweight always-on block is sourced from `claude-md/POLICY.md`. `claude-md/CLAUDE.md` is generated from that policy: never hand-edit the generated file. After changing `POLICY.md`, regenerate with:

```bash
./install.sh claude-md-print > claude-md/CLAUDE.md
```

`claude-md` install mode writes the always-on block and installs the full skill to `.claude/skills/claude-model-optimizer/`, so detailed guidance loads only when needed. `tests/sync.sh` fails CI if the generated file is stale or the policy grows beyond its lightweight boundary. Update `README.md`, `install.sh`, and tests when install modes or target paths change.

Before release, run:

```bash
tests/install.sh
tests/sync.sh
tests/codex-smoke.sh
ruby -ryaml -e 'ARGV.each { |path| text = File.read(path); m = text.match(/\A---\n(.*?)\n---\n/m) or abort("missing frontmatter: #{path}"); data = YAML.safe_load(m[1]); abort("missing name: #{path}") unless data["name"]; abort("missing description: #{path}") unless data["description"]; puts "ok #{path}: #{data["name"]}" }' skills/*/SKILL.md
git diff --check
```

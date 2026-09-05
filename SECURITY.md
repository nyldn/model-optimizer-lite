# Security Policy

## Supported Versions

This repository maintains the current Claude and Codex skill packages and their
optional helper scripts. Older snapshots are not maintained separately.

## Reporting a Vulnerability

If you find a security issue, open a private security advisory on GitHub or contact the maintainers through the repository owner.

Please do not file public issues for:

- leaked credentials
- prompt injection paths that expose secrets
- unsafe computer-use behavior that could cause real-world actions
- private research material accidentally included in a release

## Handling Secrets

Do not put secrets in:

- `CLAUDE.md`
- skill files
- issue reports
- screenshots
- transcripts
- Codex or Claude prompts

Computer-use workflows should require human confirmation for purchases, account changes, destructive actions, accepting terms, or anything with real-world consequences.

## Helper boundaries

Routing recommendations never start inference or change settings. Explicit model
discovery starts a short-lived native Codex app-server that may use provider
access and write native logs. It reads only model metadata and does not start
threads or submit prompts. Review receipts inspect local event files without
reporting their text. They validate structure, not signatures or finding accuracy.

Use receipts from trusted local runs. Do not treat a requested model, a model
name in generated text, or a user-supplied catalog as proof of actual execution.
Keep an unverified model identity visible. Unsupported or failed checks must not
silently pass or expand an agent's authority.

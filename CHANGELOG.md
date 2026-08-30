# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Each release is tagged `vX.Y.Z` in git.

## [Unreleased]

## [2.2.0] - 2026-08-29

### Added

- A dedicated installation guide covering user and project scopes, verification, updates, removal, and troubleshooting.
- Conventional `--help`, `-h`, and `help` installer commands that exit before cloning or changing files.
- A clean-room test for the same stdin execution path used by the public curl installer.
- A post-install prompt that tells users how to load the skill in a new Claude Code session.
- A progressive-disclosure Fable review-gate reference with a restricted CLI template, verified model identity, a verdict contract, and finding disposition.
- A Claude CLI help-text check for every flag used by the Fable review template.
- Deterministic fixtures that exercise the published jq filter against completed Fable reviews, fallback models, incomplete tool-use stops, and error results.

### Changed

- The README now leads with a three-step quick start and links detailed setup information instead of putting every installer caveat in the landing page.
- Fable review guidance now verifies the model on the final assistant event, rejects silent model fallbacks and incomplete tool-use stops, carries a resolution ledger across revision rounds, and reports inherited Claude worker models accurately.

## [2.1.0] - 2026-08-29

### Added

- A qualified Fable-led delegation pattern for independent, verifiable work packets, inputs larger than one useful context, and measured patterns of unusually expensive routine-work failures.
- Dynamic-workflow controls covering small-slice pilots, initial worker limits, single-level fan-out, no-progress stops, worktree isolation, and task-level cost and rework tracking.
- Routing coverage for GPT-5.6 Terra and Luna alongside Sol.

### Changed

- Codex worker effort now starts from the configured default. Sol `high` is a trial for capability-sensitive implementation, while `max` requires representative evaluation evidence.
- The Codex workflow reference now states that native Claude dynamic-workflow agents remain Claude sessions; Codex participates through MCP or a thin CLI wrapper.
- README design sources now include Anthropic's cost-optimization, Fable prompting, and dynamic-workflow guidance plus OpenAI's GPT-5.6 model guidance.

## [2.0.2] - 2026-07-27

An xhigh review of the v2.0.1 installer found that the hardening pass introduced worse failures than it fixed. Upgrade from v2.0.1 or earlier before running `claude-md` mode again.

### Fixed

- The managed-block markers are matched as whole lines. An unanchored match meant prose that merely mentioned the marker text was treated as a block opener, and every line after it was silently deleted. A file that opens a block without closing it is now a refusal with an explanation, not a truncation.
- A symlinked `CLAUDE.md` is written through rather than replaced, so a dotfiles-managed file keeps its indirection and the real target actually receives the policy block.
- `CLAUDE.md` is written with the invoking user's umask default instead of the destination's existing mode. Reading the mode of a symlink reported the link's own bits, which are 0755 on macOS and 0777 on Linux, so v2.0.1 could install a world-writable instructions file. Applying the umask default also repairs the 0600 that v2.0.0 left behind, which the previous release claimed to fix but never reached, because its no-op guard returned before the `chmod`.
- A destination that is not a regular file is refused. Previously a directory at the destination absorbed the staging file, and the installer reported success with no policy installed and a hidden orphan left behind.
- Skill backups an earlier release left inside the skills root are moved out on the next install, so the duplicate-skill condition v2.0.1 described as fixed no longer survives an upgrade.
- A skills root whose parent is not writable falls back to a temp directory for the backup instead of failing the install outright.
- A symlinked skill destination is replaced with a real copy rather than reported as already current, so deleting the checkout it pointed at can no longer remove the installed skill.
- The blank lines on both sides of a mid-file managed block are no longer merged into one extra blank line in the user's own prose.
- A staging file left by a killed run is cleared at the start of the next install, so an uncatchable termination cannot leave a copy of the user's instructions in the project indefinitely.

### Changed

- `tests/install.sh` clears inherited `FABLE5_OPTIMIZER_*` variables. Without that, a stray `FABLE5_OPTIMIZER_SKILLS_DIR` combined with v2.0.1's out-of-root backup path let the suite move a developer's real `~/.claude/skills/fable5-optimizer` aside.
- New coverage: marker text in prose, an unterminated block, a non-regular-file destination, symlink write-through for both `CLAUDE.md` and the skill folder, legacy backup migration, a backup on a content-changing rerun, and a `0604` fixture that no umask can produce, so the mode assertion cannot pass by accident.
- `README.md` gives the correct backup path for the default home install and documents marker matching, symlink handling, and the mode policy.

## [2.0.1] - 2026-07-27

### Fixed

- Skill backups no longer land inside a skills root. `install.sh` writes them to `.claude/skill-backups/` (or `~/.claude/skill-backups/`), so a backup copy can no longer be discovered as a second skill claiming the name `fable5-optimizer`.
- `claude-md` mode is now idempotent. Rerunning the installer previously appended one blank line per run before the managed block; the block is now regenerated byte-for-byte.
- An installed `.claude/CLAUDE.md` keeps its previous permissions, or the umask default for a new file, instead of inheriting `mktemp`'s `0600`.
- The file-mode probe tries GNU `stat -c` before BSD `stat -f`. On GNU, `-f` means `--file-system` and would have printed filesystem details into the captured mode, breaking the `chmod` on Linux.
- Interior whitespace-only lines in an existing `CLAUDE.md` are preserved byte for byte. Only trailing blank lines are trimmed.
- Reinstalling unchanged content is a no-op: no rewrite, no backup, and a message that says so. Previous runs created a backup on every invocation.
- The staging file for `claude-md` mode is created in the destination directory, so the final move is atomic and never crosses a filesystem boundary, and it is removed if the run fails.

### Changed

- `tests/install.sh` covers rerun idempotency, backup placement, backup suppression for unchanged content, interior whitespace preservation, and permission restore under a non-default umask.
- `install.sh` usage lists `claude-md-print` alongside the other modes.
- Corrected the Claude Code skills link in `README.md`, which pointed at the slash-commands page.

## [2.0.0] - 2026-07-27

### Added

- Claude Opus 5 as the everyday default for complex Claude Code work, with Fable 5 as the highest-capability escalation tier and Codex/GPT-5.6 Sol as an independent frontier peer.
- Progressive-disclosure Codex workflow reference covering review, bounded implementation, runtime verification, report contracts, sandboxing, model pinning, and wrapper agents.
- Current primary-source design links for Anthropic model selection, Opus 5 prompting, Claude 5 context engineering, Claude Code skills, OpenAI reasoning models, and Codex sandboxing.

### Changed

- Reworked the routing policy for the Opus 5 landscape. Multi-model loops are now optional and role-based rather than the default shape for mergeable work.
- Replaced the full always-on skill duplication with a lightweight `CLAUDE.md` router. `claude-md` install mode now installs the detailed project-local skill alongside the managed policy block.
- Updated effort guidance: Opus 5 and Fable 5 start at `high`; higher settings require a task-specific reason or evaluation evidence.
- Reframed safety as an execution-environment property. Codex review defaults to read-only, edits to workspace-limited access, and broader access requires explicit scope.
- Replaced model-personality and sticker-price claims with task-specific evaluation guidance covering quality, latency, context use, tool calls, rework, and total cost.
- Removed the non-standard `version` field from skill frontmatter; Git tags and this changelog now carry release versions.

## [1.6.0] - 2026-07-08

### Added

- Routing row for Sonnet 5: cheap in-harness Claude subagent duty (Codex wrapper agents, structured summaries, workflow glue) at low effort, with the source's caveat that Opus 4.8 is often cheaper for longer outputs because Sonnet 5 is token-hungry. The workflow wrapper pattern now names Sonnet 5 explicitly. This is the only work type the source material assigns Sonnet 5.

## [1.5.1] - 2026-07-08

### Fixed

- Skill trigger description restructured after a live headless test showed advisory phrasing ("should Claude or Codex handle reviewing this branch diff") failing to load the skill. The description now leads with a load-before-answering rule for any mention of Codex, GPT-5.5, or model-ownership questions, and names advisory question shapes explicitly. Both probe phrasings now trigger, including one with no model names at all.

## [1.5.0] - 2026-07-08

### Changed

- The always-on `CLAUDE.md` block is now generated from the skill body by `install.sh`, so an independent `claude-md` install carries the complete guidance (routing gate, effort discipline, preparedness gate, command templates, report contract, workflow wrapper pattern) instead of a hand-maintained subset.
- `claude-md/CLAUDE.md` in the repo is a generated artifact; `install.sh claude-md-print` regenerates it and `tests/sync.sh` now fails on any drift from the skill body, replacing the weaker anchor-only check.
- Skill body wording made surface-neutral so it reads correctly in both installs.

## [1.4.0] - 2026-07-08

### Added

- Effort discipline section: default Fable 5 to `high`; effort applies per step, not to run length, so `xhigh`/`max`/ultracode mostly add overthinking and cost.
- Codex-in-workflows section: thin Claude wrapper agent pattern, `gpt-5.5` label prefix, timeout/background handling, worktree isolation for parallel Codex implementers.
- Prompt-Codex-simply rule on both surfaces: brief, self-contained prompts; Codex is not Claude.
- Empty-findings rule on both surfaces: a clean review is a result, name the inspected target, do not rerun.
- Review boundaries: keep small local checks with Claude, treat Codex output as evidence not authority, add task-specific context (requirements, risky areas, tests) to review briefs.
- Orchestration-shape note: workflows for deterministic fan-out/verify; checkpoint-driven work stays in the main session with worktrees.
- Skill now also triggers when the user asks Claude to test a flow, verify UI behavior, or capture screenshots needing local automation, without naming Codex.

### Notes

- Derived from re-review of the source research material (video transcript and setup screenshots) against both surfaces.

## [1.3.0] - 2026-07-08

### Changed

- The always-on `CLAUDE.md` template is now standalone and complete: it carries the full routing policy plus the Codex command mechanics (noninteractive `codex exec`, review commands, read-only runs, report contract), so a project with only the template installed can act on the policy without the skill. Previously it was a summary that assumed the skill was present.
- Contributor docs updated: the template's rule is now "standalone first, lean second" instead of "keep it short".

## [1.2.2] - 2026-07-08

### Changed

- README rewritten in a plainer voice; the intro now presents both install surfaces (on-demand skill and always-on `CLAUDE.md` policy) instead of describing the project as a skill only.

## [1.2.1] - 2026-07-08

### Fixed

- Focused-review `codex exec` template no longer hardcodes "the uncommitted changes"; the diff target (uncommitted or against a base) is now an explicit placeholder. Found by an independent Codex review of the v1.2.0 diff.

## [1.2.0] - 2026-07-08

### Added

- Fable Preparedness Gate: three paths (active context, prepared context packet, quick checkpoint) with a compact packet field list and an anti-ceremony guard.
- Routing Gate: routine-work row, plus risk signals that force Fable 5 judgment (API/schema contracts, security surfaces, release artifacts, user-facing UI, new modules, breaking changes).
- Judgment-class rule: Codex agreement never settles architecture or taste decisions; route to Fable 5 when supervising cheaper output costs more than doing the work with Fable 5.
- Codex Report Contract: one report shape (status, files, checks, evidence, blockers) shared by review, implementation, and runtime verification.
- Fresh-context verifier briefing rule for Codex review: artifact and acceptance criteria only, never the maker's reasoning.
- Anti-pattern list for Fable-directed and Codex-delegated prompts.
- Checkpoint rule: pause only for destructive actions, real scope changes, or user-only input.
- Always-on template additions mirroring the skill: assumptions, checkable acceptance criteria, preparedness rule, no-guessing rule, checkpoint rule.
- `tests/sync.sh`: anchor sync check between the two instruction surfaces, wired into CI.
- `tests/codex-smoke.sh`: probes installed Codex CLI for the flags used by the skill's command templates (skips when codex is absent), wired into CI.
- `tests/trigger-cases.md`: manual trigger evaluation cases for the skill description.
- README install-mode chooser table.

### Fixed

- `codex review` command templates: Codex CLI 0.143.0 rejects a custom prompt combined with `--uncommitted`/`--base`; templates now use the plain form, with a read-only `codex exec` variant for focused reviews.

### Removed

- Internal review handoff prompt and internal maintainer notes moved out of the public repo; CI now blocks them from returning.

## [1.1.0] - 2026-07-08

### Added

- Always-on install surface: `claude-md/CLAUDE.md` template installed as a managed block into a project's `.claude/CLAUDE.md` via `install.sh claude-md` (idempotent, with backups).
- `tests/install.sh` covering the `skill`, `skill-project`, and `claude-md` install modes, wired into CI.
- Repo `CLAUDE.md` documenting the two-surface sync rule.

### Changed

- Tightened the skill trigger description: explicit trigger phrases plus negative triggers for ordinary implementation or review.

## [1.0.0] - 2026-07-08

### Added

- Initial public release: single `fable5-optimizer` skill routing work between Claude/Fable 5 and Codex/GPT-5.5, with review, implementation, and runtime verification command templates.
- One-shot installer (`install.sh`) with user and project modes.
- CI validation of the skill package and public boundary.

[Unreleased]: https://github.com/nyldn/fable5-optimizer/compare/v2.2.0...HEAD
[2.2.0]: https://github.com/nyldn/fable5-optimizer/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/nyldn/fable5-optimizer/compare/v2.0.2...v2.1.0
[2.0.2]: https://github.com/nyldn/fable5-optimizer/compare/v2.0.1...v2.0.2
[2.0.1]: https://github.com/nyldn/fable5-optimizer/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.6.0...v2.0.0
[1.6.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/nyldn/fable5-optimizer/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/nyldn/fable5-optimizer/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/nyldn/fable5-optimizer/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/nyldn/fable5-optimizer/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/nyldn/fable5-optimizer/releases/tag/v1.0.0

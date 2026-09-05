# Contributing

Keep Model Optimizer Lite focused on model and effort choices, compact handoffs,
and evidence-backed review. Native Claude and Codex tools execute work.

## Sources and packages

- `shared/SKILL.md` is the maintained entrypoint template.
- `shared/references/` contains shared policy and host-specific guidance.
- `shared/scripts/model_optimizer_lite.py` owns optional deterministic helpers.
- `scripts/sync-packages.py` generates the standalone package under `skills/`.
- `claude-md/POLICY.md` owns the opt-in always-on Claude block.

Never hand-edit the generated package or `claude-md/CLAUDE.md`. Regenerate them:

```sh
python3 scripts/sync-packages.py
./install.sh claude-md-print > claude-md/CLAUDE.md
```

Keep entrypoints under 700 words and the always-on policy under 250 words.
Add detail through references that load only for the relevant task.

## Validation

```sh
tests/install.sh
tests/sync.sh
python3 -m unittest discover -s tests -p '*_test.py'
tests/codex-smoke.sh
tests/claude-smoke.sh
tests/fable-review-validator.sh
git diff --check
```

Smoke checks inspect real CLI help when installed and otherwise skip. Unit tests
cover routing, receipt failures, discovery, and clean-room Codex installation.
Also exercise realistic skill requests without giving the reviewer the expected
answers. Such policy tests do not establish cost or model-quality improvements.

## Boundaries

Preserve model pins, client restrictions, user changes, and existing authority.
Do not add inference to discovery or recommendation commands. Raw transcripts,
credentials, account-specific paths, and private reports stay out of the public
package. Keep failures and missing model evidence visible.

Both hosts install `model-optimizer-lite`. Installer settings use the
`MODEL_OPTIMIZER_LITE_` prefix. Check installation and update behavior when
changing any package path.

## Releases

Move Unreleased notes into a dated semantic-version section, update compare
links, and tag the verified commit as `vX.Y.Z` after publication is authorized.
Use a minor version for additive install surfaces or helpers. Preserve old
GitHub URLs through the repository redirect when changing the project name.

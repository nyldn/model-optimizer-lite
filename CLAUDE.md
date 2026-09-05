# AI Model Optimizer project instructions

Maintain the shared sources and host-specific profiles under `shared/`.
The standalone package under `skills/ai-model-optimizer/` is generated. Both
Claude and Codex use the `ai-model-optimizer` skill name.

Read `AGENTS.md`, `CONTRIBUTING.md`, and `docs/architecture.md` for the development
contract, validation commands, and provider boundaries.

After changing shared source, run:

```sh
python3 scripts/sync-packages.py
./install.sh claude-md-print > claude-md/CLAUDE.md
tests/sync.sh
tests/install.sh
python3 -m unittest discover -s tests -p '*_test.py'
tests/codex-smoke.sh
tests/claude-smoke.sh
tests/fable-review-validator.sh
```

Do not hand-edit generated packages or the always-on template. Recommendations
must remain separate from execution, and missing model evidence must remain
unverified. Test installations only in temporary targets.

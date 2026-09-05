# Model Optimizer Lite development

Maintain the shared sources in `shared/`. Generate the standalone skill
package with `python3 scripts/sync-packages.py`; do not hand-edit package copies.
Native wrappers under `plugins/` and the marketplace catalogs are generated with
`python3 scripts/build-distribution.py`. Keep `VERSION` and all packages aligned.
Both hosts use the `model-optimizer-lite` discovery name.

Read `CONTRIBUTING.md` for validation and `docs/architecture.md` for boundaries.
Recommendation commands must not dispatch inference. Explicit discovery may
start a bounded native process; it must not start a task or change provider
settings. Preserve explicit model pins and report unavailable identity as unknown.

Keep user edits and local agent state separate from implementation commits.
Validate installation with temporary targets. Do not install into the user's
active environment or publish a release merely to test the package.

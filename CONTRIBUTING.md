# Contributing

Model Optimizer Lite is one self-contained skill. Edit
`skills/model-optimizer-lite/SKILL.md` directly. Keep ChatGPT, Codex, and Claude
guidance in that file so an installed copy does not need repository references,
scripts, generated files, or a provider CLI.

Use `skills/model-optimizer-lite/agents/openai.yaml` only for ChatGPT and Codex
display metadata. Keep it consistent with the skill name and description.

Before submitting a change, run:

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -p '*_test.py' -v
python3 scripts/validate.py
git diff --check
```

Use a virtual environment for maintainer dependencies. PyYAML is needed only
for repository checks; users of the installed skill do not need Python.

Also read the skill as a new user would. Confirm that it respects explicit model
choices, does not assume model availability, and distinguishes ChatGPT controls
from Codex CLI commands.
Also check that automatic delegation stays within an active authorized task,
respects provider restrictions, bounds child work, and reports actual execution.
Keep advice-only scenarios separate from execution scenarios in evaluations.

For changes to the skill or catalog, review [the behavior cases](tests/behavior-cases.md)
and record outcomes in the PR. Distinguish executed fresh-context cases from
prose assessments and unverified cases. Structural validation cannot prove
model-response behavior or native client discovery.

The behavior document also includes an isolated native Claude Code runner
command and fixtures. Provider-backed evaluations are maintainer checks, not
part of unattended CI.

[Upstream notes](docs/UPSTREAM.md) record the current provider documentation
and the client-version details that affect this skill.

Use the [catalog drift check](docs/CATALOG-CHECK.md) for a source-linked review
of public catalog and changelog changes. It is maintainer tooling outside the
installed skill. Its synthetic tests run in CI; network checks run manually.

Adding executable helpers, reference files, installers, plugins, generated
copies, or marketplaces is a product-scope change. Discuss that need before
reintroducing it.

Read [docs/DELIVERY.md](docs/DELIVERY.md) before changing installation, client
support, packaging, or release behavior.

# Catalog drift checks

Run this maintainer check when reviewing upstream changes:

```sh
python3 scripts/check_catalog.py
python3 scripts/check_catalog.py --format json > /tmp/model-optimizer-catalog-report.json
```

The checker reads seven public sources: OpenAI's client catalog, API catalog,
and ChatGPT/Codex changelog; Anthropic's model overview, Claude Code model
configuration and changelog, and Claude Platform release notes. Every finding
links to its source. It uses Python's standard library, requires no account or
API key, and makes no inference calls.

Exit codes are `0` for no detected changes, `1` for changes needing review, and
`2` for a fetch, extraction, baseline, or output error. A failed source is
unknown. Successful sources still appear in a partial report. JSON includes
the individual error details.

The reviewed baseline is [catalog-snapshot.json](catalog-snapshot.json), captured
on October 28, 2026, matching the skill's latest catalog review. Historical native
evaluations use their recorded skill snapshots. The baseline contains mentions and hashes,
without storing provider documentation or account data.

The checker compares normalized document text and four groups of guidance:
retirements, reasoning effort, client requirements, and skills or controls.
HTML extraction reads main content and excludes navigation, scripts, and styles.
Markdown extraction discards images and markup, reflows wrapped paragraphs, and
keeps model-page slugs. Sorting and deduplication avoid changes caused solely by
block order or repeated text. Other text changes also trigger source review.

This is a change detector. A new mention can describe an old or retired model.
A removed mention does not establish retirement. Client and API sources remain
separate, and neither proves account availability. Broad API catalogs can
mention models outside this skill's scope. Review the linked page to establish
what changed before editing the skill. A clean report does not prove semantic
correctness or native client discovery.

## Reviewing and replacing the baseline

To capture a candidate without replacing the reviewed baseline:

```sh
python3 scripts/check_catalog.py --write-candidate /tmp/model-optimizer-catalog-candidate.json
```

The candidate requires all sources to succeed. Its `reviewed_on` value is
`null`, so it cannot be used as a baseline until a maintainer reviews the
sources and sets that date. The checker refuses existing output files, the
active baseline path, and paths inside the installed skill directory.

Read changed sources, decide whether each finding affects the skill, and make
any needed guidance edits directly in `skills/model-optimizer-lite/SKILL.md`.
After reviewing the candidate, set `reviewed_on` to the review date and replace
`docs/catalog-snapshot.json` as a normal local edit. Record decisions in
[UPSTREAM.md](UPSTREAM.md). Run the repository checks and relevant behavior
cases for guidance changes. The checker never rewrites the skill or baseline,
installs anything, schedules jobs, or publishes results.

For reproducible checks without network access, save responses outside the
repository using the source IDs in `scripts/check_catalog.py`. Markdown sources
use `<source-id>.md`; HTML sources use `<source-id>.html`:

```sh
python3 scripts/check_catalog.py --source-dir /tmp/model-optimizer-sources
```

Missing saved files count as errors. Do not commit raw responses or local
reports. Ordinary CI runs the synthetic regression tests without contacting
providers. Public sites may change markup, block clients, or return negotiated
content; update extraction deliberately after reviewing a failure.

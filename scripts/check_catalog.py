#!/usr/bin/env python3
"""Compare public provider documentation with a reviewed maintainer snapshot."""

import argparse
from datetime import date, datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs/catalog-snapshot.json"
MAX_BYTES = 8 * 1024 * 1024
# Fixed public sources only. API catalogs and client catalogs remain separate.
SOURCES = {
    "openai-client": ("https://learn.chatgpt.com/docs/models", "markdown", "Models"),
    "openai-api": ("https://developers.openai.com/api/docs/models", "markdown", "Models"),
    "openai-changelog": ("https://learn.chatgpt.com/docs/changelog", "html", "changelog"),
    "claude-models": ("https://platform.claude.com/docs/en/models/overview", "html", "Claude API ID"),
    "claude-config": ("https://code.claude.com/docs/en/model-config", "html", "Model aliases"),
    "claude-changelog": ("https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md", "markdown", "Changelog"),
    "claude-release": ("https://platform.claude.com/docs/en/release-notes/overview", "html", "Release notes"),
}
CATEGORIES = {
    "retirements": r"retir|deprecat|end.of.life|sunset",
    "effort": r"effort|reasoning|ultracode|extended thinking",
    "client-requirements": r"\bversion\b|\bv?\d+\.\d+\.\d+\b|Claude Code|Codex CLI",
    "skills-and-controls": r"\bskill|\bcatalog|\bpicker|/model\b|/effort\b|switch.{0,60}context|context.{0,60}switch",
}
MODEL_ID = re.compile(r"\b(?:gpt-\d{1,2}(?:\.\d+)?(?:-[a-z][a-z0-9]*|-\d{8})*|claude-(?:opus|sonnet|haiku|fable)-\d+(?:-\d+)*)\b", re.I)
MODEL_NAME = re.compile(r"\b(?:(GPT)[- ]+|(Claude\s+)?(Opus|Sonnet|Haiku|Fable)\s+)(\d{1,2}(?!\d)(?:\.\d+)?)(?:\s+(Sol|Luna|Astra))?\b(?![\w-]|\.\d)", re.I)


class MainText(HTMLParser):
    """Read visible main content, excluding navigation and executable payloads."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.hidden = []
        self.parts = []
        self.found_main = False

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main = self.found_main = True
        if self.in_main and tag in {"script", "style", "nav", "noscript"}:
            self.hidden.append(tag)
        if self.in_main and not self.hidden and tag in {"p", "li", "tr", "h1", "h2", "h3", "h4", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.hidden and tag == self.hidden[-1]:
            self.hidden.pop()
        if tag == "main":
            self.in_main = False
        if self.in_main and not self.hidden and tag in {"p", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.in_main and not self.hidden:
            self.parts.append(data + " ")


class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urlsplit(newurl)
        if target.scheme != "https" or target.netloc != urlsplit(req.full_url).netloc:
            raise ValueError("source redirected outside its HTTPS host")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def read_source(source_id, source_dir=None):
    url, kind, _ = SOURCES[source_id]
    if source_dir is not None:
        suffix = "md" if kind == "markdown" else "html"
        with (source_dir / f"{source_id}.{suffix}").open("rb") as saved:
            data = saved.read(MAX_BYTES + 1)
    else:
        fetch_url = url + ".md" if kind == "markdown" and not url.endswith(".md") else url
        request = Request(fetch_url, headers={"User-Agent": "Mozilla/5.0 ModelOptimizerCatalogCheck/1", "Accept": "text/html" if kind == "html" else "text/markdown, text/plain"})
        with build_opener(SameHostRedirect()).open(request, timeout=15) as response:
            data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("source exceeds 8 MiB limit")
    return data.decode("utf-8")


def normalize(text, kind):
    if kind == "html":
        parser = MainText()
        parser.feed(text)
        if not parser.found_main:
            raise ValueError("HTML main content missing; extraction needs review")
        text = "".join(parser.parts)
    else:
        if re.search(r"<!doctype html|<html\b", text, re.I):
            raise ValueError("expected Markdown, received HTML")
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
        # Keep model-page slugs, but discard tracking URLs and image attributes.
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", markdown_link, text)
        # A shell heredoc such as <<EOF must not consume later documentation.
        text = re.sub(r"</?[A-Za-z][\w:-]*(?=[\s/>])[^<>]*>", "", text)
        # Reflow Markdown paragraphs; leave headings, lists, and tables separate.
        text = re.sub(r"(?<=\S)\n(?=[\w`(])", " ", text)
    return sorted({" ".join(line.split()).strip("# *\u200b") for line in text.splitlines() if line.strip()})


def markdown_link(match):
    label, url = match.groups()
    slug = re.search(r"/models/([\w.-]+)", url)
    return label + (" " + slug.group(1).removesuffix(".md") if slug else "")


def fingerprint(source_id, text):
    _, kind, sentinel = SOURCES[source_id]
    blocks = normalize(text, kind)
    joined = "\n".join(blocks)
    if len(joined) < 100 or sentinel.casefold() not in joined.casefold():
        raise ValueError("expected documentation content missing; extraction needs review")
    mentions = {match.group(0).lower().rstrip(".-") for match in MODEL_ID.finditer(joined)}
    for match in MODEL_NAME.finditer(joined):
        provider, _, family, version, tier = match.groups()
        if family:
            mentions.add("claude-" + family.lower() + "-" + version.replace(".", "-"))
        elif provider:
            mentions.add("gpt-" + version + ("-" + tier.lower() if tier else ""))
    if not mentions:
        raise ValueError("no model mentions found; extraction needs review")
    digests = {}
    for category, pattern in CATEGORIES.items():
        selected = [block for block in blocks if re.search(pattern, block, re.I)]
        digests[category] = hashlib.sha256("\n".join(selected).encode()).hexdigest()
    return {"model_mentions": sorted(mentions), "categories": digests, "content_sha256": hashlib.sha256(joined.encode()).hexdigest()}


def load_baseline(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("sources", {}).keys() != SOURCES.keys():
        raise ValueError("baseline schema or source list mismatch")
    date.fromisoformat(value["reviewed_on"])
    for source_id, entry in value["sources"].items():
        if entry.get("url") != SOURCES[source_id][0]:
            raise ValueError(f"{source_id}: baseline URL mismatch")
        mentions, categories = entry["model_mentions"], entry["categories"]
        if not isinstance(mentions, list) or not mentions or any(not isinstance(item, str) for item in mentions):
            raise ValueError(f"{source_id}: invalid baseline model mentions")
        if categories.keys() != CATEGORIES.keys() or any(not re.fullmatch(r"[a-f0-9]{64}", digest) for digest in categories.values()):
            raise ValueError(f"{source_id}: invalid baseline category hashes")
        if not re.fullmatch(r"[a-f0-9]{64}", entry["content_sha256"]):
            raise ValueError(f"{source_id}: invalid baseline content hash")
    return value


def compare(baseline, source_dir=None):
    findings, observed = [], {}
    for source_id, (url, _, _) in SOURCES.items():
        finding = {"source": source_id, "url": url}
        try:
            current = fingerprint(source_id, read_source(source_id, source_dir))
            observed[source_id] = {"url": url, **current}
            previous = baseline["sources"][source_id]
            added = sorted(set(current["model_mentions"]) - set(previous["model_mentions"]))
            removed = sorted(set(previous["model_mentions"]) - set(current["model_mentions"]))
            changed = [key for key in CATEGORIES if current["categories"][key] != previous["categories"][key]]
            content_changed = current["content_sha256"] != previous["content_sha256"]
            finding.update(status="review" if added or removed or changed or content_changed else "unchanged", added_mentions=added, removed_mentions=removed, changed_categories=changed, content_changed=content_changed)
        except (OSError, URLError, ValueError) as error:
            finding.update(status="error", error=str(error))
        findings.append(finding)
    exit_code = 2 if any(item["status"] == "error" for item in findings) else int(any(item["status"] == "review" for item in findings))
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "reviewed_on": baseline["reviewed_on"], "exit_code": exit_code, "sources": findings}
    return report, observed


def markdown_report(report):
    lines = ["# Catalog drift review", "", f"Checked {report['checked_at']}. Baseline reviewed {report['reviewed_on']}.", "", "Model mentions and changed guidance require source review. Removed mentions do not prove retirement. Public documentation does not prove account availability.", ""]
    for item in report["sources"]:
        lines.append(f"- [{item['source']}]({item['url']}): {item['status']}.")
        if item["status"] == "error":
            lines.append("  Fetch/extraction failed. See JSON output for the error; this source is unknown.")
        else:
            for field, label in (("added_mentions", "Added mentions"), ("removed_mentions", "Removed mentions"), ("changed_categories", "Changed guidance")):
                if item[field]:
                    lines.append(f"  {label}: " + ", ".join(item[field]) + ".")
            if item["content_changed"] and not item["changed_categories"]:
                lines.append("  Other documentation text changed; inspect the source.")
    return "\n".join(lines) + "\n"


def write_candidate(path, baseline_path, sources):
    target = path.resolve()
    if target == baseline_path.resolve() or target.is_relative_to(ROOT / "skills"):
        raise ValueError("candidate must be separate from the baseline and installed skill")
    candidate = {"schema_version": 1, "captured_on": date.today().isoformat(), "reviewed_on": None, "sources": sources}
    # Exclusive creation also refuses symlinks and accidental report replacement.
    with path.open("x", encoding="utf-8") as output:
        output.write(json.dumps(candidate, indent=2, sort_keys=True) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--source-dir", type=Path, help="read saved source-id.md/html files without network access")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--write-candidate", type=Path, help="write a NEW candidate file after all sources succeed; review before adopting")
    args = parser.parse_args(argv)
    try:
        report, sources = compare(load_baseline(args.baseline), args.source_dir)
        if args.write_candidate:
            if report["exit_code"] == 2:
                print("ERROR: candidate withheld because at least one source failed", file=sys.stderr)
            else:
                write_candidate(args.write_candidate, args.baseline, sources)
        print(json.dumps(report, indent=2) if args.format == "json" else markdown_report(report), end="\n" if args.format == "json" else "")
        return report["exit_code"]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

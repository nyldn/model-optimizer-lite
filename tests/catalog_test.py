"""Drift, failure, and read-only contracts using synthetic public documents."""

from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_catalog as catalog


class CatalogTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.sources = {}
        for key, (url, kind, sentinel) in catalog.SOURCES.items():
            text = f"{sentinel}\n\nThe model gpt-6.1-sol supports reasoning effort high. Model access depends on the account and client.\n\nMinimum version 2.1.284.\n"
            if kind == "html":
                text = "<main>" + "".join(f"<p>{line}</p>" for line in text.splitlines() if line) + "</main>"
            self.source_path(key).write_text(text)
            self.sources[key] = {"url": url, **catalog.fingerprint(key, text)}
        self.baseline = self.root / "baseline.json"
        self.baseline.write_text(json.dumps({"schema_version": 1, "reviewed_on": "2026-10-06", "sources": self.sources}))
        self.original = self.baseline.read_bytes()

    def source_path(self, key):
        kind = catalog.SOURCES[key][1]
        return self.root / (key + (".md" if kind == "markdown" else ".html"))

    def run_check(self, *args):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = catalog.main(["--baseline", str(self.baseline), "--source-dir", str(self.root), *args])
        self.assertEqual(self.baseline.read_bytes(), self.original)
        return code, output.getvalue(), errors.getvalue()

    def test_unchanged_and_source_linked_report(self):
        code, report, error = self.run_check()
        self.assertEqual(code, 0, error)
        for url, _, _ in catalog.SOURCES.values():
            self.assertIn(url, report)
        self.assertEqual(report.count(": unchanged."), 7)

    def test_model_addition_and_removal_are_mentions(self):
        path = self.source_path("openai-client")
        path.write_text(path.read_text().replace("gpt-6.1-sol", "gpt-7-sol"))
        code, output, _ = self.run_check("--format", "json")
        self.assertEqual(code, 1)
        finding = json.loads(output)["sources"][0]
        self.assertEqual(finding["added_mentions"], ["gpt-7-sol"])
        self.assertEqual(finding["removed_mentions"], ["gpt-6.1-sol"])

    def test_guidance_changes_without_new_model(self):
        path = self.source_path("claude-config")
        path.write_text(path.read_text().replace("effort high", "effort medium").replace("2.1.284", "2.1.300"))
        code, output, _ = self.run_check("--format", "json")
        self.assertEqual(code, 1)
        finding = next(item for item in json.loads(output)["sources"] if item["source"] == "claude-config")
        self.assertEqual(finding["added_mentions"], [])
        self.assertEqual(finding["changed_categories"], ["effort", "client-requirements"])

    def test_other_documentation_changes_still_require_review(self):
        path = self.source_path("openai-client")
        path.write_text(path.read_text() + "\n\nThe desktop application now includes a new composer control.\n")
        code, output, _ = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("Other documentation text changed", output)

    def test_html_layout_navigation_scripts_do_not_change_fingerprint(self):
        path = self.source_path("claude-config")
        before = catalog.fingerprint("claude-config", path.read_text())
        changed = '<nav>gpt-9-sol effort max</nav><script>fetch("private")</script>' + path.read_text().replace("<main>", '<main class="new"><nav>Deprecated gpt-9-sol</nav><script>gpt-9-sol</script>')
        changed = changed.replace("model gpt-6.1-sol", "model <code>gpt-6.1-sol</code>")
        self.assertEqual(before, catalog.fingerprint("claude-config", changed))

    def test_markdown_wrapping_and_model_links(self):
        text = self.source_path("openai-client").read_text()
        self.assertEqual(catalog.fingerprint("openai-client", text), catalog.fingerprint("openai-client", text.replace("supports reasoning", "supports\nreasoning")))
        text += '\n\n[GPT-6 Astra](/api/docs/models/gpt-6-astra.md)\n<img src="gpt-8-wallpaper.webp">\n'
        mentions = catalog.fingerprint("openai-client", text)["model_mentions"]
        self.assertIn("gpt-6-astra", mentions)
        self.assertFalse(any("wallpaper" in item or item.endswith(".md") for item in mentions))

    def test_markdown_heredoc_preserves_later_model_entries(self):
        text = self.source_path("claude-changelog").read_text()
        text += '\n\n- Fixed `cat > file <<EOF` display\n- Added Claude Fable 5.2 (`claude-fable-5-2`)\n- Added `--settings <file>`\n'
        mentions = catalog.fingerprint("claude-changelog", text)["model_mentions"]
        self.assertIn("claude-fable-5-2", mentions)

    def test_multiline_markdown_components_do_not_add_models(self):
        text = self.source_path("openai-client").read_text()
        component = '\n\n<ModelDetails\n  name="gpt-9-sol"\n  wallpaperUrl="/images/gpt-9-sol-texture.webp"\n/>\n'
        self.assertEqual(catalog.fingerprint("openai-client", text), catalog.fingerprint("openai-client", text + component))

    def test_adjacent_table_cells_keep_model_ids_separate(self):
        text = self.source_path("claude-models").read_text().replace("</main>", "<table><tr><td>claude-opus-5-5</td><td>claude-sonnet-5-5</td></tr></table></main>")
        mentions = catalog.fingerprint("claude-models", text)["model_mentions"]
        self.assertIn("claude-opus-5-5", mentions)
        self.assertIn("claude-sonnet-5-5", mentions)

    def test_claude_overview_accepts_current_and_previous_layouts(self):
        models = ["claude-fable-5-2", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"]
        row = "<tr><th>Claude API ID</th>" + "".join(f"<td>{model}</td>" for model in models) + "</tr>"
        for heading in ("Compare models", "Latest models"):
            with self.subTest(heading=heading):
                text = f"<main><h1>Models overview</h1><h2>{heading}</h2><table>{row}</table></main>"
                self.assertEqual(catalog.fingerprint("claude-models", text)["model_mentions"], sorted(models))

    def test_claude_overview_requires_catalog_content(self):
        padding = "Documentation is temporarily unavailable. " * 4
        for text in (
            f"<main><h1>Models overview</h1><p>claude-opus-5-5 {padding}</p></main>",
            f"<nav>Claude API ID</nav><main><p>claude-opus-5-5 {padding}</p></main>",
            f"<main><h1>Models overview</h1><p>Claude API ID {padding}</p></main>",
        ):
            with self.subTest(text=text), self.assertRaises(ValueError):
                catalog.fingerprint("claude-models", text)

    def test_repository_snapshot_matches_current_schema(self):
        self.assertEqual(len(catalog.load_baseline(catalog.BASELINE)["sources"]), 7)

    def test_error_page_and_missing_html_main_fail_closed(self):
        for text in ("<main>Access denied</main>", "<article>Model aliases gpt-6-sol effort high</article>"):
            self.source_path("claude-config").write_text(text)
            code, output, _ = self.run_check("--format", "json")
            self.assertEqual(code, 2)
            finding = next(item for item in json.loads(output)["sources"] if item["source"] == "claude-config")
            self.assertEqual(finding["status"], "error")

    def test_network_failure_does_not_claim_unchanged(self):
        with patch.object(catalog, "read_source", side_effect=URLError("unavailable")):
            report, sources = catalog.compare(catalog.load_baseline(self.baseline))
        self.assertEqual(report["exit_code"], 2)
        self.assertEqual(sources, {})
        self.assertTrue(all(item["status"] == "error" for item in report["sources"]))

    def test_malformed_baseline_is_a_clean_error(self):
        for value in ("{", "[]", '{"schema_version":99}', self.original.decode().replace('"reviewed_on": "2026-10-06"', '"reviewed_on": null')):
            self.baseline.write_text(value)
            self.original = self.baseline.read_bytes()
            code, output, error = self.run_check()
            self.assertEqual(code, 2)
            self.assertEqual(output, "")
            self.assertIn("ERROR:", error)

    def test_candidate_requires_review_and_cannot_overwrite(self):
        candidate = self.root / "candidate.json"
        code, _, error = self.run_check("--write-candidate", str(candidate))
        self.assertEqual(code, 0, error)
        self.assertIsNone(json.loads(candidate.read_text())["reviewed_on"])
        code, _, error = self.run_check("--write-candidate", str(candidate))
        self.assertEqual(code, 2)
        self.assertIn("File exists", error)
        code, _, error = self.run_check("--write-candidate", str(self.baseline))
        self.assertEqual(code, 2)
        self.assertIn("separate", error)

    def test_partial_fetch_cannot_create_candidate(self):
        self.source_path("claude-config").unlink()
        candidate = self.root / "candidate.json"
        code, _, error = self.run_check("--write-candidate", str(candidate))
        self.assertEqual(code, 2)
        self.assertIn("withheld", error)
        self.assertFalse(candidate.exists())

    def test_installed_skill_candidate_is_rejected_before_write(self):
        with self.assertRaisesRegex(ValueError, "installed skill"):
            catalog.write_candidate(catalog.ROOT / "skills/new-file.json", self.baseline, self.sources)

    def test_redirect_boundary(self):
        handler = catalog.SameHostRedirect()
        request = Request("https://learn.chatgpt.com/docs/models")
        for target in ("http://learn.chatgpt.com/docs/models", "https://example.com/", "https://user:pass@learn.chatgpt.com/"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                handler.redirect_request(request, None, 302, "Found", {}, target)
        redirected = handler.redirect_request(request, None, 302, "Found", {}, "https://learn.chatgpt.com/docs/models.md")
        self.assertEqual(redirected.full_url, "https://learn.chatgpt.com/docs/models.md")

    def test_source_size_limit_and_html_instead_of_markdown(self):
        with patch.object(catalog, "MAX_BYTES", 10), self.assertRaisesRegex(ValueError, "limit"):
            catalog.read_source("openai-client", self.root)
        with self.assertRaisesRegex(ValueError, "received HTML"):
            catalog.fingerprint("openai-client", "<!doctype html><main>Models gpt-6-sol</main>")


if __name__ == "__main__":
    unittest.main()

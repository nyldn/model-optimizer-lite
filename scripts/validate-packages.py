#!/usr/bin/env python3
"""Validate installed package boundaries, local links, and context budgets."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
for skill in (ROOT / "skills").iterdir():
    text = (skill / "SKILL.md").read_text()
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    assert frontmatter, "missing frontmatter"
    assert "name: " + skill.name in frontmatter[1], "wrong discovery name"
    assert re.search(r"^description: .+", frontmatter[1], re.M), "missing description"
    assert len(text.split()) <= 700, "entrypoint exceeds 700 words"
    assert "@NAME@" not in text and "@HOST@" not in text, "unexpanded template"
    for file in skill.rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", file.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            path = (file.parent / target.split("#")[0]).resolve()
            assert path.is_relative_to(skill.resolve()), "link escapes installed package"
            assert path.is_file(), "missing installed reference: " + target
assert len((ROOT / "claude-md/POLICY.md").read_text().split()) <= 250, "always-on policy exceeds 250 words"

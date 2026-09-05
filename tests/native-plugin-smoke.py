#!/usr/bin/env python3
"""Check native plugin installation with isolated homes and no inference."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "model-optimizer-lite"


def main():
    with tempfile.TemporaryDirectory(prefix="optimizer-native-") as directory:
        home = Path(directory)
        env = dict(os.environ, HOME=directory, CODEX_HOME=str(home / ".codex"),
                   CLAUDE_CONFIG_DIR=str(home / ".claude"), CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
        (home / ".codex").mkdir()

        def run(*command):
            return subprocess.run(command, cwd=directory, env=env, text=True,
                                  capture_output=True, check=True, timeout=45).stdout

        expected = (ROOT / "skills" / NAME / "SKILL.md").read_bytes()
        if shutil.which("codex"):
            run("codex", "plugin", "marketplace", "add", str(ROOT), "--json")
            result = json.loads(run("codex", "plugin", "add", NAME + "@" + NAME, "--json"))
            installed = Path(result["installedPath"])
            assert installed.is_relative_to(home.resolve()), "Codex wrote outside test profile"
            assert (installed / "skills" / NAME / "SKILL.md").read_bytes() == expected
            run("codex", "plugin", "remove", NAME + "@" + NAME)
            print("PASS: native Codex marketplace/install/remove; package content matches")
        else:
            print("SKIP: native Codex install check; CLI unavailable")
        if shutil.which("claude"):
            run("claude", "plugin", "validate", str(ROOT / "plugins" / NAME))
            run("claude", "plugin", "marketplace", "add", str(ROOT))
            run("claude", "plugin", "install", NAME + "@" + NAME)
            skills = list((home / ".claude/plugins").rglob("skills/" + NAME + "/SKILL.md"))
            assert skills and any(p.read_bytes() == expected for p in skills), "Claude installed skill missing"
            run("claude", "plugin", "uninstall", NAME + "@" + NAME)
            print("PASS: native Claude marketplace/install/uninstall; package content matches")
        else:
            print("SKIP: native Claude install check; CLI unavailable")


if __name__ == "__main__":
    main()

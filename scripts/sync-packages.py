#!/usr/bin/env python3
"""Build self-contained skill packages from one maintained source."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    "claude-model-optimizer": "This is the Claude entrypoint. Its existing name is retained for compatibility.",
    "ai-model-optimizer": "Use this entrypoint in Codex or another skill-capable host; select the profile for the actual host.",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = ROOT / "shared"
    failed = False
    for name, host in PACKAGES.items():
        target = ROOT / "skills" / name
        expected = {}
        for path in source.rglob("*"):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(source)
            content = path.read_bytes()
            if relative == Path("SKILL.md"):
                content = content.replace(b"@NAME@", name.encode()).replace(b"@HOST@", host.encode())
            expected[relative] = content
        for relative, content in expected.items():
            path = target / relative
            if not path.is_file() or path.read_bytes() != content:
                if args.check:
                    print("Package is stale:", path.relative_to(ROOT), file=sys.stderr)
                    failed = True
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
        if target.exists():
            for path in target.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts and path.relative_to(target) not in expected:
                    print("Unmanaged package file:", path.relative_to(ROOT), file=sys.stderr)
                    failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())

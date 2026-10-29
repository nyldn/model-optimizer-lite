#!/usr/bin/env python3
"""Validate the repository's self-contained skill."""

from pathlib import Path
import re
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_mapping(text, label):
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise ValueError(f"{label}: invalid YAML: {error}") from error
    require(isinstance(value, dict), f"{label} must be a YAML mapping")
    return value


def validate_package(root):
    skill_dir = root / "skills" / "model-optimizer-lite"
    for directory in (root / "skills", skill_dir):
        require(not directory.is_symlink(), f"symlink not allowed: {directory.relative_to(root)}")
        require(directory.is_dir(), f"missing directory: {directory.relative_to(root)}")
    actual = set()
    for path in skill_dir.rglob("*"):
        require(not path.is_symlink(), f"symlink not allowed: {path.relative_to(root)}")
        if path.is_file():
            actual.add(path.relative_to(skill_dir))
    expected = {Path("SKILL.md"), Path("agents/openai.yaml")}
    require(actual == expected, f"unexpected installed files: {sorted(map(str, actual ^ expected))}")
    return skill_dir


def validate_skill(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    require(match is not None, "SKILL.md frontmatter is missing or incomplete")
    frontmatter = load_mapping(match.group(1), "SKILL.md frontmatter")
    runtime_overrides = {"model", "effort", "context", "agent", "hooks", "allowed-tools", "disallowed-tools"} & frontmatter.keys()
    require(not runtime_overrides, f"skill frontmatter cannot set unconditional runtime overrides: {sorted(runtime_overrides)}")
    require(frontmatter.get("name") == "model-optimizer-lite", "unexpected skill name")
    description = frontmatter.get("description")
    require(isinstance(description, str) and bool(description.strip()), "description must be a nonempty string")
    metadata = frontmatter.get("metadata")
    require(isinstance(metadata, dict), "skill metadata must be a mapping")
    require(metadata.get("version") == "6.0.0", "unexpected skill version")
    require(metadata.get("source") == "https://github.com/nyldn/model-optimizer-lite", "unexpected skill source")
    require(bool(text[match.end():].strip()), "SKILL.md instructions must not be empty")
    require(len(text.splitlines()) <= 140, "SKILL.md should remain compact")
    require("references/" not in text and "scripts/" not in text, "installed skill must be self-contained")


def validate_ui(path):
    metadata = load_mapping(path.read_text(encoding="utf-8"), "openai.yaml")
    interface = metadata.get("interface")
    require(isinstance(interface, dict), "openai.yaml interface must be a mapping")
    require(interface.get("display_name") == "Model Optimizer Lite", "unexpected display name")
    require(interface.get("short_description") == "Choose the right model and reasoning effort", "unexpected short description")
    prompt = interface.get("default_prompt")
    require(isinstance(prompt, str) and "$model-optimizer-lite" in prompt, "default_prompt must invoke $model-optimizer-lite")


def validate_public_files(root):
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout
    candidates = [value.decode() for value in listed.split(b"\0") if value]
    blocked_paths = (
        re.compile(r"(^|/)research/"),
        re.compile(r"(^|/)Docs/"),
        re.compile(r"(^|/)\.claude/"),
        re.compile(r"\.(png|jpe?g|webp|gif|mov|mp4)$", re.IGNORECASE),
    )
    blocked_names = {"transcript.md", "example-claude.md", "internal-notes.md", "FABLE5_HANDOFF.md"}
    for relative in candidates:
        name = Path(relative).name
        secret_env = name.startswith(".env") and name != ".env.example"
        blocked = secret_env or name in blocked_names or any(pattern.search(relative) for pattern in blocked_paths)
        require(not blocked, f"blocked file present: {relative}")


def validate(root=ROOT):
    skill_dir = validate_package(root)
    validate_skill(skill_dir / "SKILL.md")
    validate_ui(skill_dir / "agents" / "openai.yaml")
    validate_public_files(root)


def main():
    try:
        validate()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: self-contained skill validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

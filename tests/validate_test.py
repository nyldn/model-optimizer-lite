"""Regression tests for the public validator contract using isolated repositories."""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ValidatorTest(unittest.TestCase):
    def setUp(self):
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name) / "repo"
        self.root.mkdir()
        shutil.copytree(ROOT / "skills", self.root / "skills")
        shutil.copytree(ROOT / "scripts", self.root / "scripts")
        shutil.copy2(ROOT / ".gitignore", self.root / ".gitignore")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.skill_dir = self.root / "skills/model-optimizer-lite"
        self.skill = self.skill_dir / "SKILL.md"
        self.ui = self.skill_dir / "agents/openai.yaml"

    def run_validator(self, expected_error=None, optimized=False):
        env = os.environ.copy()
        env.pop("PYTHONOPTIMIZE", None)
        command = [sys.executable]
        if optimized:
            command.append("-O")
        result = subprocess.run(
            command + ["scripts/validate.py"],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
        )
        if expected_error is None:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("OK:", result.stdout)
        else:
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(expected_error, result.stderr)
            self.assertNotIn("OK:", result.stdout)

    def test_current_package_passes(self):
        self.run_validator()
        self.run_validator(optimized=True)

    def test_frontmatter_requires_valid_yaml_and_types(self):
        original = self.skill.read_text()
        for description, error in (
            ('"unterminated', "invalid YAML"),
            ("[]", "description must be a nonempty string"),
            ('""', "description must be a nonempty string"),
            ("null", "description must be a nonempty string"),
        ):
            with self.subTest(description=description):
                lines = original.splitlines()
                lines[2] = "description: " + description
                self.skill.write_text("\n".join(lines) + "\n")
                self.run_validator(error)

    def test_yaml_must_be_a_mapping(self):
        self.skill.write_text("---\n- name: model-optimizer-lite\n---\nInstructions\n")
        self.run_validator("frontmatter must be a YAML mapping")

    def test_metadata_must_be_a_mapping(self):
        self.skill.write_text(self.skill.read_text().replace("metadata:", "other:", 1))
        self.run_validator("skill metadata must be a mapping")

    def write_instructions(self, instructions):
        header, separator, _ = self.skill.read_text().partition("\n---\n")
        self.assertTrue(separator)
        self.skill.write_text(header + separator + instructions + "\n")

    def test_empty_instructions_fail(self):
        self.write_instructions("")
        self.run_validator("instructions must not be empty")

    def test_frontmatter_cannot_unconditionally_override_runtime(self):
        original = self.skill.read_text()
        for field, value in (
            ("model", "opus"), ("effort", "max"), ("context", "fork"),
            ("agent", "Explore"), ("hooks", "{}"), ("allowed-tools", "Bash"),
            ("disallowed-tools", "Bash"),
        ):
            with self.subTest(field=field):
                self.skill.write_text(original.replace("name: model-optimizer-lite\n", f"name: model-optimizer-lite\n{field}: {value}\n", 1))
                self.run_validator("skill frontmatter cannot set unconditional runtime overrides")

    def test_ui_requires_parsed_fields(self):
        original = self.ui.read_text()
        for value, error in (
            ("\n".join("# " + line for line in original.splitlines()), "must be a YAML mapping"),
            (original + 'broken: "unterminated\n', "invalid YAML"),
            (original.replace("interface:", "appearance:", 1), "interface must be a mapping"),
            (original.replace('default_prompt: "', 'unused: "', 1), "default_prompt must invoke"),
            (original + "  default_prompt: []\n", "default_prompt must invoke"),
        ):
            with self.subTest(error=error):
                self.ui.write_text(value + "\n")
                self.run_validator(error)

    def test_file_symlinks_fail(self):
        external = self.root.parent / "external-skill.md"
        shutil.copy2(self.skill, external)
        self.skill.unlink()
        for target in (external, self.root.parent / "missing.md"):
            with self.subTest(target=target.name):
                self.skill.symlink_to(target)
                self.run_validator("symlink not allowed")
                self.skill.unlink()

    def test_directory_symlinks_fail(self):
        for path in (self.skill_dir / "agents", self.skill_dir, self.root / "skills"):
            with self.subTest(path=path.name):
                external = self.root.parent / "external-directory"
                path.rename(external)
                path.symlink_to(external, target_is_directory=True)
                self.run_validator("symlink not allowed")
                path.unlink()
                external.rename(path)

    def test_unexpected_files_fail_even_when_optimized(self):
        (self.skill_dir / "helper.py").write_text('print("unexpected executable")\n')
        self.run_validator("unexpected installed files")
        self.run_validator("unexpected installed files", optimized=True)

    def test_missing_required_file_fails(self):
        self.ui.unlink()
        self.run_validator("unexpected installed files")

    def test_instruction_references_fail_even_when_optimized(self):
        self.write_instructions("Read scripts/helper.py.")
        self.run_validator("must be self-contained", optimized=True)

    def test_blocked_tracked_files_fail_even_when_optimized(self):
        for relative in (".env", "research/private.md", ".claude/settings.json"):
            with self.subTest(path=relative):
                path = self.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("test fixture, no private data\n")
                subprocess.run(["git", "add", "-f", relative], cwd=self.root, check=True)
                self.run_validator("blocked file present", optimized=True)
                subprocess.run(["git", "rm", "-f", "--cached", relative], cwd=self.root, check=True, capture_output=True)
                path.unlink()


if __name__ == "__main__":
    unittest.main()

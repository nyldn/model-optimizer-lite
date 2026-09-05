import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def install_environment(**overrides):
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("AI_MODEL_OPTIMIZER_")}
    env.update(overrides)
    return env


class CodexInstallTests(unittest.TestCase):
    def test_user_install_is_standalone_idempotent_and_preserves_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env = install_environment(HOME=directory)
            command = [str(ROOT / "install.sh"), "codex"]
            subprocess.run(command, cwd=directory, env=env, check=True, capture_output=True)
            skill = home / ".agents/skills/ai-model-optimizer"
            self.assertTrue((skill / "SKILL.md").is_file())
            self.assertFalse((home / ".claude").exists())
            self.assertFalse((home / ".codex/config.toml").exists())
            self.assertTrue((skill / "references/shared-policy.md").is_file())
            helper = skill / "scripts/model_optimizer.py"
            subprocess.run(["python3", str(helper), "route", "--host", "codex", "--task", "review"],
                           cwd=directory, check=True, capture_output=True)
            before = (skill / "SKILL.md").stat().st_mtime_ns
            subprocess.run(command, cwd=directory, env=env, check=True, capture_output=True)
            self.assertEqual(before, (skill / "SKILL.md").stat().st_mtime_ns)
            (skill / "custom.md").write_text("preserve this")
            subprocess.run(command, cwd=directory, env=env, check=True, capture_output=True)
            backups = list((home / ".agents/skill-backups").glob("*/custom.md"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "preserve this")

    def test_project_install_honors_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            env = install_environment(HOME=directory, AI_MODEL_OPTIMIZER_TARGET=str(target))
            subprocess.run([str(ROOT / "install.sh"), "codex-project"], cwd=directory, env=env,
                           check=True, capture_output=True)
            self.assertTrue((target / ".agents/skills/ai-model-optimizer/SKILL.md").is_file())
            self.assertFalse((target / "AGENTS.md").exists())

    def test_both_hosts_install_identical_package_at_custom_roots(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            claude_root = home / "claude skills"
            codex_root = home / "codex skills"
            env = install_environment(
                HOME=directory,
                AI_MODEL_OPTIMIZER_CLAUDE_SKILLS_DIR=str(claude_root),
                AI_MODEL_OPTIMIZER_CODEX_SKILLS_DIR=str(codex_root),
            )
            for mode, invocation in (("skill", "/ai-model-optimizer"),
                                     ("codex", "$ai-model-optimizer")):
                output = subprocess.run([str(ROOT / "install.sh"), mode], env=env,
                                        cwd=directory, check=True, capture_output=True, text=True)
                self.assertIn(invocation, output.stdout)
            def package_files(root):
                return {path.relative_to(root): path.read_bytes()
                        for path in root.rglob("*") if path.is_file()}
            self.assertEqual(package_files(claude_root), package_files(codex_root))
            self.assertIn(b"name: ai-model-optimizer\n",
                          (claude_root / "ai-model-optimizer/SKILL.md").read_bytes())
            self.assertFalse((home / ".claude").exists())
            self.assertFalse((home / ".agents").exists())

    def test_custom_policy_path_and_mode_preserve_surrounding_instructions(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / "project"
            policy = home / "custom rules.md"
            policy.write_text("Keep these instructions.\n")
            env = install_environment(
                HOME=directory, AI_MODEL_OPTIMIZER_TARGET=str(target),
                AI_MODEL_OPTIMIZER_CLAUDE_MD=str(policy), AI_MODEL_OPTIMIZER_MODE="claude-md",
            )
            command = [str(ROOT / "install.sh")]
            subprocess.run(command, env=env, cwd=directory, check=True, capture_output=True)
            first = policy.read_bytes()
            self.assertTrue(first.startswith(b"Keep these instructions.\n"))
            self.assertIn(b"<!-- ai-model-optimizer:start -->", first)
            self.assertTrue((target / ".claude/skills/ai-model-optimizer/SKILL.md").is_file())
            self.assertFalse((target / ".claude/CLAUDE.md").exists())
            subprocess.run(command, env=env, cwd=directory, check=True, capture_output=True)
            self.assertEqual(first, policy.read_bytes())


if __name__ == "__main__":
    unittest.main()

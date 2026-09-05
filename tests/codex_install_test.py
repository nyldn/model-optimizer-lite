import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CodexInstallTests(unittest.TestCase):
    def test_user_install_is_standalone_idempotent_and_preserves_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            env = dict(os.environ, HOME=directory)
            env.pop("AI_MODEL_OPTIMIZER_CODEX_SKILLS_DIR", None)
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
            env = dict(os.environ, AI_MODEL_OPTIMIZER_TARGET=str(target))
            subprocess.run([str(ROOT / "install.sh"), "codex-project"], cwd=directory, env=env,
                           check=True, capture_output=True)
            self.assertTrue((target / ".agents/skills/ai-model-optimizer/SKILL.md").is_file())
            self.assertFalse((target / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()

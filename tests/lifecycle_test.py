import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "model-optimizer-lite"


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("MODEL_OPTIMIZER_LITE_")}
        self.env.update(HOME=str(self.home), MODEL_OPTIMIZER_LITE_TARGET=str(self.home / "project"))

    def run_installer(self, *args, check=True, script=None):
        result = subprocess.run([str(script or ROOT / "install.sh"), *args], env=self.env,
                                cwd=self.home, text=True, capture_output=True, timeout=20,
                                start_new_session=True)
        if check:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_install_both_status_corruption_and_recoverable_removal(self):
        self.run_installer("both")
        self.assertIn("files verified", self.run_installer("status").stdout)
        claude = self.home / ".claude/skills" / NAME
        codex = self.home / ".agents/skills" / NAME
        (claude / "SKILL.md").write_text("my changes")
        status = self.run_installer("status", check=False)
        self.assertEqual(status.returncode, 1)
        self.assertIn("modified", status.stdout)
        unrelated = self.home / ".claude/skills/other/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("leave alone")
        self.run_installer("uninstall", "both")
        self.assertFalse(claude.exists())
        self.assertFalse(codex.exists())
        backups = list((self.home / ".claude/skill-backups").glob("*/SKILL.md"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "my changes")
        self.assertEqual(unrelated.read_text(), "leave alone")
        self.run_installer("uninstall", "both")

    def test_status_and_invalid_input_do_not_download_or_create_files(self):
        self.env["MODEL_OPTIMIZER_LITE_REPO_URL"] = "invalid://must-not-fetch"
        for args in [("status",), ("uninstall",), ("bogus",), ("claude", "--bogus"), ()]:
            result = self.run_installer(*args, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Cloning", result.stderr)
            self.assertEqual(list(self.home.iterdir()), [])

    def test_project_uninstall_removes_only_own_policy_and_preserves_symlink(self):
        target = self.home / "project"
        policy = self.home / "rules.md"
        policy.write_text("House rules.\n")
        (target / ".claude").mkdir(parents=True)
        (target / ".claude/CLAUDE.md").symlink_to(policy)
        self.run_installer("claude-md")
        self.run_installer("uninstall", "claude", "--project")
        self.assertTrue((target / ".claude/CLAUDE.md").is_symlink())
        self.assertEqual(policy.read_text(), "House rules.\n")
        self.assertFalse((target / ".claude/skills" / NAME).exists())
        self.assertFalse((self.home / ".claude").exists())

    def test_broken_policy_refuses_uninstall_before_archiving_skill(self):
        self.run_installer("claude", "--project")
        target = self.home / "project"
        policy = target / ".claude/CLAUDE.md"
        policy.write_text("<!-- model-optimizer-lite:start -->\nKeep me.\n")
        result = self.run_installer("uninstall", "claude", "--project", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((target / ".claude/skills" / NAME).exists())
        self.assertIn("Keep me.", policy.read_text())

    def test_update_fetches_fresh_source_and_skips_uninstalled_host(self):
        self.run_installer("claude")
        remote = self.home / "remote"
        shutil.copytree(ROOT / "skills", remote / "skills", ignore=shutil.ignore_patterns("__pycache__"))
        skill = remote / "skills" / NAME
        (skill / "VERSION").write_text("99.0.0\n")
        files = sorted(p for p in skill.rglob("*") if p.is_file() and p.name != "FILES.sha256")
        (skill / "FILES.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() +
            "  " + p.relative_to(skill).as_posix() + "\n" for p in files))
        for command in [["init", "-q"], ["add", "."], ["-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm", "fixture"]]:
            subprocess.run(["git", "-C", str(remote), *command], check=True, capture_output=True)
        self.env["MODEL_OPTIMIZER_LITE_REPO_URL"] = remote.as_uri()
        self.run_installer("update", "both")
        self.assertEqual((self.home / ".claude/skills" / NAME / "VERSION").read_text(), "99.0.0\n")
        self.assertFalse((self.home / ".agents").exists())
        self.assertNotEqual((ROOT / "VERSION").read_text(), "99.0.0\n")

    def test_failed_download_keeps_current_installation(self):
        self.run_installer("claude")
        skill = self.home / ".claude/skills" / NAME / "SKILL.md"
        before = skill.read_bytes()
        self.env["MODEL_OPTIMIZER_LITE_REPO_URL"] = str(self.home / "missing")
        self.assertNotEqual(self.run_installer("update", "claude", check=False).returncode, 0)
        self.assertEqual(skill.read_bytes(), before)

    def test_update_refreshes_existing_project_policy(self):
        self.run_installer("claude-md")
        target = self.home / "project"
        policy = target / ".claude/CLAUDE.md"
        policy.write_text("Project rule.\n\n" + policy.read_text())
        remote = self.home / "remote"
        shutil.copytree(ROOT / "skills", remote / "skills", ignore=shutil.ignore_patterns("__pycache__"))
        (remote / "claude-md").mkdir()
        (remote / "claude-md/POLICY.md").write_text("Updated policy fixture.\n")
        for command in [["init", "-q"], ["add", "."], ["-c", "user.name=Test", "-c",
                        "user.email=test@example.invalid", "commit", "-qm", "fixture"]]:
            subprocess.run(["git", "-C", str(remote), *command], check=True, capture_output=True)
        self.env["MODEL_OPTIMIZER_LITE_REPO_URL"] = remote.as_uri()
        self.run_installer("update", "claude", "--project")
        self.assertIn("Updated policy fixture.", policy.read_text())
        self.assertTrue(policy.read_text().startswith("Project rule.\n"))
        self.assertEqual(policy.read_text().count("model-optimizer-lite:start"), 1)

    def test_failed_copy_does_not_report_success_or_remove_existing_install(self):
        self.run_installer("claude")
        skill = self.home / ".claude/skills" / NAME / "SKILL.md"
        skill.write_text("preserve my edit")
        bin_dir = self.home / "bin"
        bin_dir.mkdir()
        for name in ["rsync", "cp"]:
            path = bin_dir / name
            path.write_text("#!/bin/sh\nexit 1\n")
            path.chmod(0o755)
        self.env["PATH"] = str(bin_dir) + os.pathsep + self.env["PATH"]
        result = self.run_installer("claude", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("installed and", result.stdout)
        self.assertEqual(skill.read_text(), "preserve my edit")


class DistributionTests(unittest.TestCase):
    def test_bootstrap_uses_release_archive_without_git_or_provider_clis(self):
        spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/build-distribution.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            output = home / "assets"
            module.build_archives(output)
            bootstrap = home / "install.sh"
            shutil.copy2(ROOT / "install.sh", bootstrap)
            bin_dir = home / "bin"
            bin_dir.mkdir()
            curl = bin_dir / "curl"
            curl.write_text('''#!/bin/sh
printf '%s\\n' "$@" >> "$CURL_LOG"
while [ "$#" -gt 0 ]; do
  if [ "$1" = -o ]; then shift; /bin/cp "$SOURCE_FIXTURE" "$1"; exit; fi
  shift
done
exit 1
''')
            curl.chmod(0o755)
            for name in ["git", "codex", "claude", "python3"]:
                path = bin_dir / name
                path.write_text("#!/bin/sh\necho 'unexpected dependency' >&2\nexit 99\n")
                path.chmod(0o755)
            env = {k: v for k, v in os.environ.items() if not k.startswith("MODEL_OPTIMIZER_LITE_")}
            env.update(HOME=directory, PATH=str(bin_dir) + os.pathsep + env["PATH"],
                       SOURCE_FIXTURE=str(output / (NAME + "-source.tar.gz")), CURL_LOG=str(home / "curl.log"))
            subprocess.run([str(bootstrap), "both"], env=env, cwd=directory,
                           check=True, capture_output=True, timeout=20)
            self.assertIn("/releases/latest/download/", (home / "curl.log").read_text())
            for app in [".claude", ".agents"]:
                self.assertEqual((home / app / "skills" / NAME / "SKILL.md").read_bytes(),
                                 (ROOT / "skills" / NAME / "SKILL.md").read_bytes())

    def test_archives_are_reproducible_and_skill_upload_has_one_root(self):
        spec = importlib.util.spec_from_file_location("distribution", ROOT / "scripts/build-distribution.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            module.build_archives(a)
            module.build_archives(b)
            self.assertEqual({p.name: p.read_bytes() for p in a.iterdir()},
                             {p.name: p.read_bytes() for p in b.iterdir()})
            with zipfile.ZipFile(a / (NAME + ".zip")) as archive:
                self.assertTrue(all(p.startswith(NAME + "/") for p in archive.namelist()))
                self.assertEqual(archive.read(NAME + "/SKILL.md"),
                                 (ROOT / "skills" / NAME / "SKILL.md").read_bytes())
                self.assertFalse(any("__pycache__" in p or ".git/" in p for p in archive.namelist()))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Generate native plugin packages and reproducible release downloads."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "model-optimizer-lite"
URL = "https://github.com/nyldn/" + NAME


def json_bytes(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def skill_files():
    root = ROOT / "skills" / NAME
    return {p.relative_to(root): p.read_bytes() for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def generated_files():
    version = (ROOT / "VERSION").read_text().strip()
    manifest = {
        "name": NAME, "version": version,
        "description": "Choose a model, carry context into a handoff, and check review evidence.",
        "author": {"name": "nyldn", "url": "https://github.com/nyldn"},
        "homepage": URL, "repository": URL, "license": "MIT", "skills": "./skills/",
    }
    codex_manifest = dict(manifest, interface={
        "displayName": "Model Optimizer Lite",
        "shortDescription": "Help choosing which AI to use for the job.",
        "longDescription": "Model advice and handoffs for Claude and Codex. No background service or automatic model switching.",
        "developerName": "nyldn", "category": "Productivity", "capabilities": [],
        "defaultPrompt": ["Should I keep my current model for this task?"],
    })
    plugin = Path("plugins") / NAME
    files = {plugin / "skills" / NAME / p: content for p, content in skill_files().items()}
    files[plugin / ".codex-plugin/plugin.json"] = json_bytes(codex_manifest)
    files[plugin / ".claude-plugin/plugin.json"] = json_bytes(manifest)
    files[plugin / "LICENSE"] = (ROOT / "LICENSE").read_bytes()
    files[Path(".agents/plugins/marketplace.json")] = json_bytes({
        "name": NAME, "interface": {"displayName": "Model Optimizer Lite"},
        "plugins": [{"name": NAME, "source": {"source": "local", "path": "./plugins/" + NAME},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": "Productivity"}],
    })
    files[Path(".claude-plugin/marketplace.json")] = json_bytes({
        "name": NAME, "owner": {"name": "nyldn"},
        "plugins": [{"name": NAME, "source": "./plugins/" + NAME,
                     "description": manifest["description"]}],
    })
    return files


def write_zip(path, files):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)


def build_archives(output):
    output.mkdir(parents=True, exist_ok=True)
    skill = skill_files()
    write_zip(output / (NAME + ".zip"), {NAME + "/" + p.as_posix(): b for p, b in skill.items()})
    plugin_root = Path("plugins") / NAME
    plugin = {NAME + "/" + p.relative_to(plugin_root).as_posix(): b
              for p, b in generated_files().items() if p.is_relative_to(plugin_root)}
    write_zip(output / (NAME + "-plugin.zip"), plugin)
    source = {"skills/" + NAME + "/" + p.as_posix(): b for p, b in skill.items()}
    for name in ["install.sh", "VERSION", "LICENSE", "claude-md/POLICY.md"]:
        source[name] = (ROOT / name).read_bytes()
    with (output / (NAME + "-source.tar.gz")).open("wb") as stream:
        with gzip.GzipFile(filename="", fileobj=stream, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                for name, data in sorted(source.items()):
                    entry = tarfile.TarInfo(NAME + "/" + name)
                    entry.size = len(data)
                    entry.mode = 0o755 if name == "install.sh" else 0o644
                    archive.addfile(entry, io.BytesIO(data))
    (output / "install.sh").write_bytes((ROOT / "install.sh").read_bytes())
    assets = [NAME + ".zip", NAME + "-plugin.zip", NAME + "-source.tar.gz", "install.sh"]
    (output / "SHA256SUMS").write_text("".join(
        hashlib.sha256((output / name).read_bytes()).hexdigest() + "  " + name + "\n" for name in assets))
    print("Built skill ZIP, plugin ZIP, source archive, installer, and checksums in", output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--archives", type=Path)
    args = parser.parse_args()
    subprocess.run(["python3", str(ROOT / "scripts/sync-packages.py"), "--check"], check=True)
    expected = generated_files()
    stale = []
    for relative, content in expected.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != content:
            if args.check:
                stale.append(str(relative))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    plugin_root = ROOT / "plugins" / NAME
    if plugin_root.exists():
        for path in plugin_root.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.relative_to(ROOT) not in expected:
                stale.append("Unexpected plugin file: " + str(path.relative_to(ROOT)))
    if stale:
        parser.exit(1, "Distribution differs from source:\n" + "\n".join(stale) + "\n")
    if args.archives:
        build_archives(args.archives)


if __name__ == "__main__":
    main()

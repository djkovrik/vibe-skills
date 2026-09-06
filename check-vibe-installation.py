#!/usr/bin/env python3
"""Compare the installed skill package with its manifest and current source bytes."""
import argparse
import json
import os
from pathlib import Path


def health(package, destination):
    manifest = json.loads((package / "vibe-skills-manifest.json").read_text(encoding="utf-8-sig"))
    entries = []
    for name in manifest["skillDirectories"]:
        source, installed = package/name, destination/name
        missing = []; changed = []
        if not installed.is_dir():
            entries.append({"skill":name, "status":"missing", "path":str(installed)}); continue
        for path in source.rglob("*"):
            if not path.is_file() or any(p in {"__pycache__", ".test-workspaces"} for p in path.parts): continue
            relative = path.relative_to(source)
            target = installed/relative
            if not target.is_file(): missing.append(relative.as_posix())
            elif target.read_bytes() != path.read_bytes(): changed.append(relative.as_posix())
        entries.append({"skill":name, "status":"current" if not missing and not changed else "stale", "path":str(installed),
            "missingFiles":missing, "changedFiles":changed})
    return {"healthy":all(i["status"]=="current" for i in entries), "skills":entries,
        "discovery":"Filesystem parity checked; the host refreshes skill discovery on the next turn."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home()/".codex"))/"skills")
    args = parser.parse_args(); result = health(Path(__file__).resolve().parent, args.destination.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2)); raise SystemExit(0 if result["healthy"] else 1)

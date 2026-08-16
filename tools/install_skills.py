#!/usr/bin/env python3
"""Install repository Skills into a local agent Skill directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Parent directory that will contain Skill folders")
    parser.add_argument("--skill", action="append", help="Install only named Skill; repeatable")
    parser.add_argument("--force", action="store_true", help="Replace an existing same-name Skill")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source_root = root / "skills"
    target_root = Path(args.target).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    requested = set(args.skill or [])
    sources = sorted(path for path in source_root.iterdir() if (path / "SKILL.md").exists())
    if requested:
        sources = [path for path in sources if path.name in requested]
        missing = requested - {path.name for path in sources}
        if missing:
            raise SystemExit(f"Unknown Skill(s): {', '.join(sorted(missing))}")
    for source in sources:
        destination = (target_root / source.name).resolve()
        if target_root not in destination.parents:
            raise SystemExit(f"Refusing destination outside target root: {destination}")
        if destination.exists():
            if not args.force:
                raise SystemExit(f"Refusing to replace existing Skill: {destination}")
            shutil.rmtree(destination)
        shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        print(f"Installed {source.name} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

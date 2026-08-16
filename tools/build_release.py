#!/usr/bin/env python3
"""Build a deterministic, public-boundary-checked source ZIP and SHA-256 file."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {".git", ".venv", "__pycache__"}
FORBIDDEN_SUFFIXES = {".exe", ".dll", ".msi", ".lic", ".key", ".pem", ".zip", ".7z"}


def checked(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    checked([sys.executable, str(ROOT / "tools" / "validate_repository.py")])
    checked([sys.executable, str(ROOT / "tools" / "run_evals.py")])
    checked([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])

    listing = subprocess.run(
        ["git", "ls-files", "--cached"], cwd=ROOT, check=True, text=True, capture_output=True
    ).stdout.splitlines()
    if not listing:
        raise SystemExit("No files are staged/tracked; run git add -A before packaging.")
    files = []
    for name in sorted(listing):
        path = ROOT / name
        if not path.is_file():
            raise SystemExit(f"Tracked file missing from working tree: {name}")
        if any(part in FORBIDDEN_PARTS for part in Path(name).parts):
            raise SystemExit(f"Forbidden path in release: {name}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise SystemExit(f"Forbidden file type in release: {name}")
        files.append((name.replace("\\", "/"), path))

    output_dir = ROOT.parent / "packages"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"ayu-scicompute-v{version}.zip"
    prefix = f"ayu-scicompute-v{version}/"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name, path in files:
            info = zipfile.ZipInfo(prefix + name, date_time=(2026, 8, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, path.read_bytes())

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="ascii")
    print(f"RELEASE PACKAGE: {archive}")
    print(f"SHA256: {digest}")
    print(f"FILES: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

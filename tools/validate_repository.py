#!/usr/bin/env python3
"""Self-contained public-release audit for the Skill repository."""

from __future__ import annotations

import py_compile
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
IGNORED = {".git", ".venv", "__pycache__"}
BINARY_EXTENSIONS = {".exe", ".dll", ".msi", ".zip", ".7z", ".tar", ".gz", ".lic"}
FORBIDDEN_FILENAMES = {"POTCAR", "WAVECAR", "CHGCAR"}
SECRET_PATTERNS = [
    re.compile("github_" + r"pat_[A-Za-z0-9_]+"),
    re.compile("gh" + r"p_[A-Za-z0-9]+"),
    re.compile(r"BEGIN (?:RSA|OPENSSH|EC) PRIVATE KEY"),
    re.compile("sk" + r"-[A-Za-z0-9]{20,}"),
    re.compile("AKIA" + r"[A-Z0-9]{16}"),
]
PRIVATE_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:\\" + "Users" + r"\\[^\\\s]+\\"),
    re.compile("/" + "home" + r"/[^/\s]+/"),
]
UNFINISHED_MARKER = "TO" + "DO"


def files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not any(part in IGNORED for part in path.parts):
            yield path


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("missing YAML frontmatter")
    raw = text[4:text.index("\n---\n", 4)]
    fields = {}
    for line in raw.splitlines():
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1); fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    errors = []
    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    for skill in skill_dirs:
        skill_file = skill / "SKILL.md"
        if not skill_file.exists():
            errors.append(f"missing SKILL.md: {skill}"); continue
        try:
            fields = parse_frontmatter(skill_file)
            if set(fields) != {"name", "description"}: errors.append(f"frontmatter fields must be name+description only: {skill.name}")
            if fields.get("name") != skill.name: errors.append(f"folder/name mismatch: {skill.name}")
            if not fields.get("description"): errors.append(f"empty description: {skill.name}")
        except Exception as exc:
            errors.append(f"{skill.name}: {exc}")
    for path in files():
        relative = path.relative_to(ROOT)
        if path.name.upper() in FORBIDDEN_FILENAMES: errors.append(f"forbidden licensed/large engine artifact: {relative}")
        if path.suffix.lower() in BINARY_EXTENSIONS: errors.append(f"forbidden bundled binary/archive: {relative}")
        if path.stat().st_size > 5_000_000: errors.append(f"file exceeds 5 MB: {relative}")
        if path.suffix.lower() in {".md", ".py", ".ps1", ".pl", ".json", ".yaml", ".yml", ".cff", ".txt"}:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if UNFINISHED_MARKER in text and relative.name != "RELEASE_CHECKLIST.md": errors.append(f"unfinished marker remains: {relative}")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text): errors.append(f"possible secret: {relative}")
            for pattern in PRIVATE_PATH_PATTERNS:
                if pattern.search(text): errors.append(f"possible personal absolute path: {relative}")
            if path.suffix.lower() == ".py":
                unsafe_tokens = ("shell=" + "True", "pickle." + "loads(", "yaml." + "load(")
                for token in unsafe_tokens:
                    if token in text: errors.append(f"review unsafe Python construct '{token}': {relative}")
        if path.suffix.lower() == ".json":
            try: json.loads(path.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError as exc: errors.append(f"invalid JSON {relative}: {exc}")
        if path.suffix.lower() == ".py":
            try: py_compile.compile(str(path), doraise=True)
            except py_compile.PyCompileError as exc: errors.append(f"Python compile failed {relative}: {exc}")
    if errors:
        print("REPOSITORY VALIDATION FAILED")
        for error in errors: print(f"- {error}")
        return 2
    print(f"REPOSITORY VALIDATION PASSED: {len(skill_dirs)} Skills, public-boundary checks clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render a conservative ORCA 6 input from a JSON manifest and XYZ structure."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PRESETS = {
    "fast-opt": ["r2SCAN-3c", "Opt", "TightSCF"],
    "dft-opt-freq": [
        "PBE0",
        "D4",
        "def2-TZVP",
        "def2/J",
        "RIJCOSX",
        "Opt",
        "Freq",
        "TightSCF",
    ],
    "frontier-esp": [
        "PBE0",
        "D4",
        "def2-TZVP",
        "def2/J",
        "RIJCOSX",
        "TightSCF",
        "CHELPG",
    ],
    "single-point": [
        "PBE0",
        "D4",
        "def2-TZVP",
        "def2/J",
        "RIJCOSX",
        "TightSCF",
    ],
}

ATOM_LINE = re.compile(
    r"^\s*([A-Z][a-z]?)\s+"
    r"([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s+"
    r"([-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?)\s*$"
)


def read_xyz(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 3:
        raise ValueError("XYZ file is too short")
    try:
        count = int(lines[0].strip())
    except ValueError as exc:
        raise ValueError("XYZ first line must be the atom count") from exc
    atom_lines = lines[2 : 2 + count]
    if len(atom_lines) != count:
        raise ValueError("XYZ atom count does not match coordinate lines")
    for line in atom_lines:
        if not ATOM_LINE.match(line):
            raise ValueError(f"invalid XYZ atom line: {line}")
    return atom_lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    xyz_path = Path(data["xyz"])
    if not xyz_path.is_absolute():
        xyz_path = (manifest_path.parent / xyz_path).resolve()
    atom_lines = read_xyz(xyz_path)

    charge = data.get("charge")
    multiplicity = data.get("multiplicity")
    if charge is None or multiplicity is None:
        raise SystemExit("charge and multiplicity are required")
    charge = int(charge)
    multiplicity = int(multiplicity)
    if multiplicity < 1:
        raise SystemExit("multiplicity must be positive")
    nprocs = int(data.get("nprocs", 1))
    maxcore = int(data.get("maxcore_mb_per_core", 2000))
    if nprocs < 1 or maxcore < 256:
        raise SystemExit("nprocs must be >=1 and maxcore_mb_per_core must be >=256")

    preset = data.get("preset", "single-point")
    if preset not in PRESETS:
        raise SystemExit(f"unknown preset {preset}; choose from {sorted(PRESETS)}")
    keywords = list(PRESETS[preset])
    keywords.extend(str(item) for item in data.get("extra_keywords", []))
    solvent = data.get("solvent")
    if solvent:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", str(solvent)):
            raise SystemExit("solvent must be a simple ORCA solvent identifier")
        keywords.append(f"CPCM({solvent})")

    name = str(data.get("name", xyz_path.stem))
    content = [
        f"# Generated for {name}; verify method against the scientific task",
        "! " + " ".join(keywords),
        "",
        "%pal",
        f"  nprocs {nprocs}",
        "end",
        f"%maxcore {maxcore}",
        "",
        f"* xyz {charge} {multiplicity}",
        *atom_lines,
        "*",
        "",
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(content), encoding="utf-8", newline="\n")
    record = {
        "output": str(output.resolve()),
        "xyz": str(xyz_path),
        "preset": preset,
        "charge": charge,
        "multiplicity": multiplicity,
        "nprocs": nprocs,
        "maxcore_mb_per_core": maxcore,
        "estimated_orca_memory_mb": nprocs * maxcore,
        "keywords": keywords,
    }
    print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

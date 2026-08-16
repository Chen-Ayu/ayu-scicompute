#!/usr/bin/env python3
"""Extract conservative summary data from an ORCA text output."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ENERGY_RE = re.compile(r"FINAL SINGLE POINT ENERGY\s+(-?\d+\.\d+)")
ORBITAL_RE = re.compile(
    r"^\s*\d+\s+([0-9]+(?:\.[0-9]+)?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s*$",
    re.MULTILINE,
)
FREQ_RE = re.compile(r"(-?\d+(?:\.\d+)?)\s*cm\*\*-1")
DIPOLE_RE = re.compile(r"Magnitude \(Debye\)\s*:\s*([0-9.]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", required=True)
    parser.add_argument("--summary")
    args = parser.parse_args()
    path = Path(args.output_file).resolve()
    text = path.read_text(encoding="utf-8", errors="replace")

    energies = [float(value) for value in ENERGY_RE.findall(text)]
    occupied = []
    virtual = []
    for occ_text, _eh_text, ev_text in ORBITAL_RE.findall(text):
        occupancy = float(occ_text)
        energy_ev = float(ev_text)
        if occupancy > 0.01:
            occupied.append(energy_ev)
        else:
            virtual.append(energy_ev)
    homo = max(occupied) if occupied else None
    lumo = min(virtual) if virtual else None
    gap = lumo - homo if homo is not None and lumo is not None else None

    frequencies = [float(value) for value in FREQ_RE.findall(text)]
    imaginary = [value for value in frequencies if value < -20.0]
    dipoles = [float(value) for value in DIPOLE_RE.findall(text)]
    normal = "ORCA TERMINATED NORMALLY" in text
    opt_requested = bool(
        re.search(
            r"^\s*(?:\|\s*\d+>\s*)?![^\r\n]*\bOpt\b",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
    )
    frequency_requested = bool(
        re.search(
            r"^\s*(?:\|\s*\d+>\s*)?![^\r\n]*\bFreq\b",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
    )
    opt_converged = "THE OPTIMIZATION HAS CONVERGED" in text
    scf_failed = (
        "SCF NOT CONVERGED" in text
        or "ORCA finished by error termination" in text
        or "aborting the run" in text.lower()
    )
    scientific_gate_passed = (
        normal
        and not scf_failed
        and (not opt_requested or opt_converged)
        and (not frequency_requested or bool(frequencies))
    )
    status = "completed" if scientific_gate_passed else "incomplete-or-failed"
    summary = {
        "engine": "orca",
        "output_file": str(path),
        "status": status,
        "normal_termination": normal,
        "scf_failure_detected": scf_failed,
        "optimization_requested_detected": opt_requested,
        "optimization_converged": opt_converged,
        "frequency_requested_detected": frequency_requested,
        "scientific_gate_passed": scientific_gate_passed,
        "final_single_point_energy_hartree": energies[-1] if energies else None,
        "homo_ev": homo,
        "lumo_ev": lumo,
        "gap_ev": gap,
        "dipole_debye": dipoles[-1] if dipoles else None,
        "frequency_count": len(frequencies),
        "imaginary_frequencies_below_minus_20_cm-1": imaginary,
        "quality_notes": [],
    }
    if normal and opt_requested and not opt_converged:
        summary["quality_notes"].append("Optimization convergence marker not found.")
    if frequencies and imaginary:
        summary["quality_notes"].append(
            "Significant imaginary frequencies detected; do not call this a minimum."
        )
    if frequency_requested and not frequencies:
        summary["quality_notes"].append("Frequency task detected but no frequencies were extracted.")
    if homo is None or lumo is None:
        summary["quality_notes"].append("Frontier orbitals were not extracted.")
    summary_path = Path(args.summary) if args.summary else path.with_suffix(".summary.json")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

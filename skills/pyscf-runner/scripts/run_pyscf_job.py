#!/usr/bin/env python3
"""Execute a manifest-driven PySCF molecular calculation and emit a strict summary."""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

HARTREE_TO_EV = 27.211386245988
PRESETS = {
    "pbe0-def2-svp": {"family": "dft", "xc": "pbe0", "basis": "def2-svp"},
    "pbe0-def2-tzvp": {"family": "dft", "xc": "pbe0", "basis": "def2-tzvp"},
    "b3lyp-def2-svp": {"family": "dft", "xc": "b3lyp", "basis": "def2-svp"},
    "hf-def2-svp": {"family": "hf", "xc": None, "basis": "def2-svp"},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_xyz(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if len(lines) < 3:
        raise ValueError("XYZ file is too short")
    count = int(lines[0].strip())
    atoms = [line.strip() for line in lines[2:2 + count] if line.strip()]
    if len(atoms) != count or len(lines[2:]) < count:
        raise ValueError("XYZ atom count does not match coordinates")
    for line in atoms:
        fields = line.split()
        if len(fields) != 4:
            raise ValueError(f"Invalid XYZ coordinate line: {line}")
        float(fields[1]); float(fields[2]); float(fields[3])
    return atoms


def dump_xyz(mol, path: Path, comment: str) -> None:
    coords = mol.atom_coords(unit="Angstrom")
    lines = [str(mol.natm), comment]
    for index in range(mol.natm):
        symbol = mol.atom_pure_symbol(index)
        x, y, z = coords[index]
        lines.append(f"{symbol:<2} {x: .10f} {y: .10f} {z: .10f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_method(mol, settings: dict):
    from pyscf import dft, scf
    family = settings["family"].lower()
    open_shell = mol.spin != 0
    if family == "dft":
        mf = dft.UKS(mol) if open_shell else dft.RKS(mol)
        mf.xc = settings["xc"]
        mf.grids.level = int(settings.get("grid_level", 3))
    elif family == "hf":
        mf = scf.UHF(mol) if open_shell else scf.RHF(mol)
    else:
        raise ValueError("method.family must be dft or hf")
    mf.max_cycle = int(settings.get("max_cycle", 120))
    mf.conv_tol = float(settings.get("conv_tol", 1e-9))
    if settings.get("density_fit", False):
        mf = mf.density_fit()
    epsilon = settings.get("solvent_epsilon")
    if epsilon is not None:
        mf = mf.ddCOSMO()
        mf.with_solvent.eps = float(epsilon)
    return mf


def frontier(mf) -> dict:
    import numpy as np
    energies = mf.mo_energy
    occupations = mf.mo_occ
    channels = []
    if isinstance(energies, (tuple, list)) or getattr(energies, "ndim", 1) == 2:
        for label, e, occ in zip(("alpha", "beta"), energies, occupations):
            occupied = np.where(np.asarray(occ) > 0)[0]
            virtual = np.where(np.asarray(occ) == 0)[0]
            channels.append((label, e, occupied, virtual))
    else:
        e = np.asarray(energies); occ = np.asarray(occupations)
        channels.append(("restricted", e, np.where(occ > 0)[0], np.where(occ == 0)[0]))
    result = {"orbital_channels": {}}
    all_homo = []; all_lumo = []
    for label, values, occupied, virtual in channels:
        if not len(occupied) or not len(virtual):
            raise RuntimeError(f"Cannot identify HOMO/LUMO for {label} channel")
        homo_index = int(occupied[-1]); lumo_index = int(virtual[0])
        homo = float(values[homo_index] * HARTREE_TO_EV)
        lumo = float(values[lumo_index] * HARTREE_TO_EV)
        result["orbital_channels"][label] = {
            "homo_index_zero_based": homo_index,
            "lumo_index_zero_based": lumo_index,
            "homo_ev": homo,
            "lumo_ev": lumo,
            "gap_ev": lumo - homo,
        }
        all_homo.append((homo, label, homo_index)); all_lumo.append((lumo, label, lumo_index))
    homo, homo_label, homo_index = max(all_homo)
    lumo, lumo_label, lumo_index = min(all_lumo)
    result.update({
        "homo_ev": homo, "lumo_ev": lumo, "gap_ev": lumo - homo,
        "homo_channel": homo_label, "lumo_channel": lumo_label,
        "homo_index_zero_based": homo_index, "lumo_index_zero_based": lumo_index,
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve(); run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(args.manifest).resolve()
    data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    state_path = run_dir / "pyscf_job_state.json"
    summary_path = run_dir / "pyscf_summary.json"
    state = {"engine": "pyscf", "status": "running", "pid": os.getpid(), "started_at": now(), "manifest": str(manifest_path)}
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    summary = {"engine": "pyscf", "name": data.get("name", "case"), "status": "failed", "normal_termination": False, "quality_notes": []}
    try:
        import numpy as np
        import pyscf
        from pyscf import gto
        from pyscf.hessian import thermo
        from pyscf.tools import cubegen

        xyz_path = Path(data["xyz"])
        if not xyz_path.is_absolute(): xyz_path = (manifest_path.parent / xyz_path).resolve()
        atoms = read_xyz(xyz_path)
        charge = int(data["charge"]); multiplicity = int(data["multiplicity"])
        if multiplicity < 1: raise ValueError("multiplicity must be positive")
        electron_count = sum(gto.charge(line.split()[0]) for line in atoms) - charge
        spin = multiplicity - 1
        if electron_count < 1:
            raise ValueError("molecule must contain at least one electron")
        if spin > electron_count or (electron_count - spin) % 2:
            raise ValueError(
                f"charge/multiplicity parity is inconsistent: {electron_count} electrons, multiplicity {multiplicity}"
            )
        resources = data.get("resources", {})
        threads = int(resources.get("threads", 1)); memory_mb = int(resources.get("memory_mb", 2000))
        if threads < 1 or memory_mb < 256: raise ValueError("invalid resources")
        pyscf.lib.num_threads(threads)
        preset = data.get("preset", "pbe0-def2-svp")
        if preset not in PRESETS: raise ValueError(f"unknown preset: {preset}")
        settings = {**PRESETS[preset], **data.get("method", {})}
        mol = gto.M(atom="\n".join(atoms), unit="Angstrom", charge=charge, spin=spin,
                    basis=settings["basis"], verbose=4, max_memory=memory_mb)
        task = data.get("task", "single-point")
        allowed = {"single-point", "frontier-esp", "geometry-opt", "frequency", "opt-freq"}
        if task not in allowed: raise ValueError(f"unsupported task: {task}")
        mf = build_method(mol, settings); mf.chkfile = str(run_dir / "pyscf.chk")
        energy = float(mf.kernel())
        if not mf.converged: raise RuntimeError("SCF did not converge")
        optimization_requested = task in {"geometry-opt", "opt-freq"}
        optimization_converged = False
        if optimization_requested:
            optimizer = mf.Gradients().optimizer(solver="geomeTRIC")
            mol = optimizer.kernel()
            optimization_converged = bool(getattr(optimizer, "converged", False))
            if not optimization_converged: raise RuntimeError("geometry optimization did not converge")
            dump_xyz(mol, run_dir / "optimized.xyz", "PySCF optimized geometry")
            mf = build_method(mol, settings); mf.chkfile = str(run_dir / "pyscf.chk")
            energy = float(mf.kernel())
            if not mf.converged: raise RuntimeError("post-optimization SCF did not converge")
        result = frontier(mf)
        dm = mf.make_rdm1()
        dm_array = np.asarray(dm)
        dm_total = dm_array.sum(axis=0) if dm_array.ndim == 3 else dm
        charges = mf.mulliken_pop(mol, dm, verbose=0)[1]
        result["mulliken_charges_e"] = [float(value) for value in np.asarray(charges)]
        frequency_requested = task in {"frequency", "opt-freq"}
        if frequency_requested:
            hessian = mf.Hessian().kernel()
            analysis = thermo.harmonic_analysis(mol, hessian)
            frequencies = analysis["freq_wavenumber"]
            result["frequencies_cm-1"] = [
                -float(abs(np.imag(value))) if abs(np.imag(value)) > 1e-8 else float(np.real(value))
                for value in frequencies
            ]
            result["imaginary_frequencies_below_minus_20_cm-1"] = [value for value in result["frequencies_cm-1"] if value < -20.0]
        cube = data.get("cube", {})
        properties = set(cube.get("properties", []))
        resolution = float(cube.get("resolution_bohr", 0.35)); margin = float(cube.get("margin_bohr", 3.0))
        if not 0.05 <= resolution <= 2.0:
            raise ValueError("cube.resolution_bohr must be between 0.05 and 2.0")
        if not 0.0 <= margin <= 20.0:
            raise ValueError("cube.margin_bohr must be between 0.0 and 20.0")
        generated = []
        if "density" in properties:
            path = run_dir / "density.cube"; cubegen.density(mol, str(path), dm_total, resolution=resolution, margin=margin); generated.append(path.name)
        if "mep" in properties:
            path = run_dir / "mep.cube"; cubegen.mep(mol, str(path), dm_total, resolution=resolution, margin=margin); generated.append(path.name)
        if "homo" in properties or "lumo" in properties:
            coeff = mf.mo_coeff
            if isinstance(coeff, (tuple, list)) or getattr(coeff, "ndim", 2) == 3:
                channel_map = {"alpha": 0, "beta": 1}
                homo_coeff = coeff[channel_map[result["homo_channel"]]][:, result["homo_index_zero_based"]]
                lumo_coeff = coeff[channel_map[result["lumo_channel"]]][:, result["lumo_index_zero_based"]]
            else:
                homo_coeff = coeff[:, result["homo_index_zero_based"]]; lumo_coeff = coeff[:, result["lumo_index_zero_based"]]
            if "homo" in properties:
                path = run_dir / "homo.cube"; cubegen.orbital(mol, str(path), homo_coeff, resolution=resolution, margin=margin); generated.append(path.name)
            if "lumo" in properties:
                path = run_dir / "lumo.cube"; cubegen.orbital(mol, str(path), lumo_coeff, resolution=resolution, margin=margin); generated.append(path.name)
        summary.update(result)
        summary.update({
            "status": "completed", "normal_termination": True, "scf_converged": True,
            "scientific_gate_passed": True,
            "optimization_requested": optimization_requested, "optimization_converged": optimization_converged,
            "frequency_requested": frequency_requested, "final_single_point_energy_hartree": energy,
            "charge": charge, "multiplicity": multiplicity, "task": task, "preset": preset,
            "method": settings, "pyscf_version": pyscf.__version__, "python_version": platform.python_version(),
            "xyz": str(xyz_path), "generated_files": generated,
        })
        print("PYSCF_TASK_COMPLETED")
        return_code = 0
    except Exception as exc:
        summary["error_type"] = type(exc).__name__; summary["error"] = str(exc)
        summary["traceback"] = traceback.format_exc()
        print("PYSCF_TASK_FAILED", file=sys.stderr); traceback.print_exc()
        return_code = 2
    finally:
        summary["finished_at"] = now()
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        state.update({"status": summary["status"], "updated_at": now(), "summary": str(summary_path)})
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())

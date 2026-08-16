---
name: pyscf-runner
description: Run open-source PySCF molecular and finite-cluster quantum chemistry for gels, biomass, lignin, cellulose fragments, monomers, additives, ions, solvation, and binding complexes. Use when an agent must validate charge and multiplicity, run HF or DFT single points, geometry optimization, harmonic frequencies, HOMO/LUMO, Mulliken charges, density/orbital/electrostatic-potential cubes, or consistent binding-energy cycles, monitor real execution, enforce convergence, and deliver traceable machine-readable results.
---

# PySCF Runner

Use PySCF as the default open-source numerical backend for finite molecules and clusters. Do not use a finite cluster as an undocumented substitute for a periodic gel.

## Run sequence

1. Run `scripts/preflight_pyscf.py` with the Python interpreter intended for the job.
2. Validate XYZ structure, protonation, charge, multiplicity, solvent model, and requested properties.
3. Read [references/pyscf-methods.md](references/pyscf-methods.md) and record a defensible method.
4. Copy `assets/pyscf-job.example.json` into a dedicated run directory and edit it.
5. Launch through `scripts/launch_pyscf_job.ps1` on Windows or call `scripts/run_pyscf_job.py` directly.
6. Monitor `pyscf_job_state.json`, stdout/stderr, and `pyscf_summary.json`.
7. Apply [references/pyscf-quality-gates.md](references/pyscf-quality-gates.md).

## Boundaries

- Require charge and multiplicity; never change either merely to obtain convergence.
- Use unrestricted KS/HF for nonzero spin and label spin channels.
- Treat frontier orbital energies as method-dependent descriptors.
- Treat the generated MEP cube as a spatial electrostatic-potential field, not CHELPG atomic charges.
- Keep the same method, basis, solvent, and geometry convention throughout a binding-energy cycle.
- Require an optimizer convergence flag before calling a geometry optimized.
- Require frequencies before calling an optimized structure a verified minimum when minimum character matters.

Read [references/execution-runbook.md](references/execution-runbook.md) completely when the host is not Codex or execution fails.

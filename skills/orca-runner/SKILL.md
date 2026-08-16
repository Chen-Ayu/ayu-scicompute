---
name: orca-runner
description: Operate local ORCA for finite molecular and cluster quantum-chemistry calculations relevant to gels, biomass, lignin, cellulose fragments, monomers, additives, ions, and binding complexes. Use when Codex must validate charge and multiplicity, generate ORCA 6 input for single-point energy, geometry optimization, frequency, HOMO/LUMO, CHELPG/ESP, solvation, or binding-energy tasks, launch and monitor orca.exe, parse normal termination and convergence, extract energies and frontier orbitals, diagnose SCF or optimization failures, and deliver traceable results.
---

# ORCA Runner

Use ORCA as the numerical engine for finite molecules and clusters. Do not use it as a replacement for large periodic gel MD.

## Non-Codex entry

If the runtime does not natively load this skill, read [references/windows-execution-runbook.md](references/windows-execution-runbook.md) completely. Require local PowerShell, filesystem, and process tools. A chat-only model may prepare an `.inp` file but cannot run ORCA.

## Run sequence

1. Run `scripts/preflight_orca.ps1`. Confirm the executable and helper programs.
2. Validate atom identities, geometry, charge, multiplicity, solvent, and requested properties.
3. Read [references/orca-methods.md](references/orca-methods.md) and select a defensible preset or explicit method.
4. Create a manifest based on `assets/orca-job.example.json`.
5. Render the input with `scripts/render_orca_input.py`.
6. Launch with `scripts/run_orca_job.ps1`; use the full ORCA executable path and a dedicated run directory.
7. Monitor with `scripts/monitor_orca_job.ps1`.
8. Parse with `scripts/parse_orca_output.py`.
9. Apply [references/orca-quality-gates.md](references/orca-quality-gates.md).

## Engine discovery

- Accept an explicit `-OrcaExe` path, then `ORCA_EXE`, then an `orca.exe` available on `PATH`.
- Require helper programs such as `orca_plot.exe`, `orca_2mkl.exe`, `orca_chelpg.exe`, or `orca_vpot.exe` only when the requested property needs them.
- Never distribute ORCA binaries or license files with this skill. Read [references/license-boundary.md](references/license-boundary.md) before public redistribution.

Re-probe before each campaign. Do not assume that executable presence proves a valid parallel runtime or sufficient memory.

## Scientific boundaries

- Require charge and multiplicity before launch.
- Use the same method, basis, solvent model, and geometry convention throughout a binding-energy cycle.
- Run frequencies before calling an optimized geometry a minimum when thermochemistry or minimum character matters.
- Distinguish CHELPG atomic charges from a spatial ESP cube or mapped surface.
- Generate orbital or ESP cube files only from a normally terminated calculation and document the grid/surface settings.
- Treat frontier orbital energies and gaps as method-dependent descriptors.

## Failure handling

Use [references/orca-failures.md](references/orca-failures.md). Change one justified convergence control at a time, preserve the failed input/output, and never hide a failed case from the final table.

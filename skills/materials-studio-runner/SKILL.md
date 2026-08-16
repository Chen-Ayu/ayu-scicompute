---
name: materials-studio-runner
description: Interoperate with a user-installed and user-licensed BIOVIA Materials Studio environment through MaterialsScript and RunMatScript for gel, hydrogel, polymer, biomass, lignin, cellulose, packing, conformer, DMol3, Forcite, Amorphous Cell, and molecular-dynamics workflows. Use when an agent must preflight the runner and Gateway, generate independent Perl jobs, launch or resume real calculations, monitor logs, parse HOMO/LUMO, energy, ESP-field, optimization, or MD outputs, diagnose failures, and deliver traceable evidence without bundling or bypassing proprietary software.
---

# Materials Studio Runner

Use this interoperability adapter only with a user-authorized Materials Studio installation. Never distribute vendor binaries, installers, manuals, license files, or vendor assets. Read [references/license-boundary.md](references/license-boundary.md).

## Run sequence

1. Resolve `RunMatScript.bat` from an explicit parameter or `MATERIALS_STUDIO_RUNNER`.
2. Run `scripts/preflight_ms.ps1` and confirm runner, Gateway, writable storage, and a user-authorized installation.
3. Smoke-test a new machine state with `assets/ms-script-smoke.pl` in a disposable run directory.
4. Read [references/ms-methods.md](references/ms-methods.md) and validate chemistry, force-field typing, charge states, and reference states.
5. Render a routine script with `scripts/render_ms_job.py`, or adapt a documented independent pattern using [references/materialsscript-patterns.md](references/materialsscript-patterns.md).
6. Launch with `scripts/run_ms_job.ps1`; use background mode for long work.
7. Monitor expected stage markers with `scripts/monitor_ms_job.ps1`.
8. Parse result tables with `scripts/parse_ms_results.py` and apply [references/ms-quality-gates.md](references/ms-quality-gates.md).

## Boundaries

- A found executable does not prove a valid license seat or scientific method.
- Never attempt activation, license bypass, seat circumvention, or license-server modification.
- Preserve source XSD/XTD/MOL/CAR/MDF and run only in a dedicated project directory.
- Stage non-ASCII paths through an ASCII temporary directory when the installed server requires it.
- Do not call a job complete from exit code or output-file existence alone.
- Verify density/potential fields before promising an ESP visualization.
- Treat every version-sensitive MaterialsScript property as requiring a disposable probe.

Read [references/windows-execution-runbook.md](references/windows-execution-runbook.md) completely when the host is not Codex or launch fails.

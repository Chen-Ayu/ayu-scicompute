# Independent MaterialsScript patterns

Use the smallest applicable pattern and parameterize all chemistry through a manifest.

- Print explicit start, per-stage, per-case failure, and final markers.
- Wrap each case in `eval`; keep failed rows in the result table.
- Resolve documents by copied run-directory filenames, never private workspace paths.
- Preserve inputs and save generated structures under new names.
- Record module, settings, force field, charge, multiplicity, temperature, pressure, timestep, step count, and random seed as applicable.
- For packing/MD, separate build, minimization, heating, density equilibration, production, and analysis.
- For binding energy, use one consistent engine/method/reference convention.

Required marker examples:

- `MS_TASK_START`
- `FORCITE_OPT_DONE <case>`
- `DMOL3_SP_DONE <case>`
- `NPT_DONE <case>`
- `PRODUCTION_DONE <case>`
- `MS_TASK_ALL_DONE`

Do not publish scripts copied from confidential projects or vendor examples unless redistribution rights are confirmed.

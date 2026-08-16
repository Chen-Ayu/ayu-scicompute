# ORCA Windows Execution Runbook

Read this file completely when the host model is not Codex.

## Engine layout

- Resolve the executable from the `-OrcaExe` parameter, `ORCA_EXE`, or `orca.exe` on `PATH`.
- Detect and record the installed ORCA version instead of assuming one.
- Detect `mpiexec.exe` on `PATH` before parallel jobs.
- Locate helper programs beside the resolved ORCA executable.

ORCA is a command-line program. Do not try to open it like a normal graphical application.

## 1. Confirm runtime capability

The agent must be able to:

- read/write the run directory;
- execute PowerShell;
- start the resolved ORCA executable;
- wait or monitor a background PID;
- read `.out` and generated files.

Without these tools, prepare input only and tell the user the exact launch command.

## 2. Run preflight

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<ORCA_SKILL>\scripts\preflight_orca.ps1" `
  -OrcaExe "<ORCA_EXE>" `
  -OutputJson "<PROJECT>\00_request\orca_preflight.json"
```

Require:

- `orca_exists = true`;
- all helpers required by the requested property exist;
- `ready_for_serial_smoke = true`;
- `ready_for_parallel_smoke = true` before a parallel job.

Executable presence does not prove that a method fits memory.

## 3. Validate the structure

For XYZ input:

1. first line is the atom count;
2. second line is a comment;
3. exactly that many coordinate lines follow;
4. every coordinate line contains element, x, y, z;
5. units are angstrom;
6. geometry has no duplicated or overlapping atoms;
7. chemical identity, hydrogens, protonation, and counterions are documented.

Determine:

- total formal charge;
- spin multiplicity;
- whether an unrestricted treatment is chemically expected;
- whether the finite cluster is a defensible model of the gel/biomass environment.

Do not guess a radical or ionic state merely to make ORCA run.

## 4. Create the manifest

Copy `assets/orca-job.example.json` into the project run directory and edit:

```json
{
  "name": "case_name",
  "xyz": "case.xyz",
  "charge": 0,
  "multiplicity": 1,
  "preset": "frontier-esp",
  "nprocs": 4,
  "maxcore_mb_per_core": 2000,
  "solvent": null,
  "extra_keywords": []
}
```

`%maxcore` is memory per ORCA process. Estimated requested ORCA memory is approximately:

`nprocs * maxcore_mb_per_core`

Detect available memory and leave capacity for Windows and other programs. Do not assign all physical memory to ORCA.

## 5. Select a preset

Read `orca-methods.md`.

- `fast-opt`: efficient geometry preparation.
- `dft-opt-freq`: hybrid DFT optimization and frequency.
- `frontier-esp`: single-point frontier orbitals plus CHELPG charges.
- `single-point`: consistent energy evaluation.

For flexible biomass fragments, do not run an expensive method on one arbitrary conformation and call it representative.

For anions, diffuse systems, metals, open-shell states, or suspected multireference chemistry, stop and reconsider the method/basis instead of blindly using the preset.

## 6. Render the input

```powershell
<PYTHON> "<ORCA_SKILL>\scripts\render_orca_input.py" `
  --manifest "<RUN_DIR>\manifest.json" `
  --output "<RUN_DIR>\case.inp"
```

The renderer validates XYZ count/format, charge, multiplicity, processor count, memory, preset, and solvent identifier.

Open and inspect the `.inp`. Confirm:

- `!` keyword line;
- `%pal nprocs`;
- `%maxcore`;
- `* xyz <charge> <multiplicity>`;
- all atoms;
- closing `*`.

## 7. Dry-run the launcher

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<ORCA_SKILL>\scripts\run_orca_job.ps1" `
  -RunDir "<RUN_DIR>" `
  -InputFile "case.inp" `
  -OrcaExe "<ORCA_EXE>" `
  -DryRun
```

Inspect `orca_job_state.json`. It must show the full executable, input, output, and run directory.

## 8. Launch

Foreground:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<ORCA_SKILL>\scripts\run_orca_job.ps1" `
  -RunDir "<RUN_DIR>" `
  -InputFile "case.inp" `
  -OrcaExe "<ORCA_EXE>"
```

Background:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<ORCA_SKILL>\scripts\run_orca_job.ps1" `
  -RunDir "<RUN_DIR>" `
  -InputFile "case.inp" `
  -OrcaExe "<ORCA_EXE>" `
  -Background
```

The launcher prepends the resolved ORCA directory to `PATH` for helper discovery and redirects stdout/stderr into the run directory.

## 9. Monitor

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<ORCA_SKILL>\scripts\monitor_orca_job.ps1" `
  -RunDir "<RUN_DIR>" `
  -OutputFile "<RUN_DIR>\case.out" `
  -OutputJson "<RUN_DIR>\monitor.json"
```

Interpret:

- `running`: PID is active and normal termination is not yet present;
- `completed`: `ORCA TERMINATED NORMALLY` is present and known fatal markers are absent;
- `incomplete-or-failed`: output exists but the process ended without normal termination;
- `not-started`: no readable output.

Do not use output-file existence alone as proof of completion.

## 10. Parse

```powershell
<PYTHON> "<ORCA_SKILL>\scripts\parse_orca_output.py" `
  --output-file "<RUN_DIR>\case.out" `
  --summary "<RUN_DIR>\case.summary.json"
```

Inspect:

- `normal_termination`;
- `scf_failure_detected`;
- `optimization_converged`;
- `final_single_point_energy_hartree`;
- `homo_ev`;
- `lumo_ev`;
- `gap_ev`;
- `dipole_debye`;
- imaginary frequencies;
- `quality_notes`.

The parser intentionally leaves unavailable properties as `null`; never fill them from memory or expectation.

## 11. Optimization and frequency rules

For a claimed optimized minimum require:

- normal termination;
- optimization-converged marker;
- final optimized geometry;
- no scientifically significant imaginary frequencies when a frequency job was requested.

If optimization failed, do not run/report frequency, ESP, or frontier properties as though the intended minimum had been reached.

## 12. HOMO/LUMO

Report:

- geometry source;
- charge and multiplicity;
- functional and basis;
- dispersion;
- solvent;
- HOMO and LUMO in eV;
- gap in eV;
- restricted/unrestricted treatment.

For unrestricted calculations, inspect alpha and beta orbital sections explicitly. Do not hide spin dependence behind one unlabeled gap.

## 13. CHELPG versus spatial ESP

The `frontier-esp` preset requests `CHELPG`, which yields electrostatic-potential-fitted atomic charges when successful.

This is not automatically a colored ESP surface.

For a spatial ESP:

1. require a normally terminated job and `.gbw`;
2. use an ORCA 6.1-compatible, verified `orca_plot`/`orca_vpot` workflow;
3. preserve every helper command and generated grid/cube;
4. map the ESP cube onto a consistent electron-density isosurface in a visualization tool;
5. use the same grid, isovalue, and color scale across compared molecules.

The current skill does not silently drive the interactive `orca_plot` menu. If the runtime cannot automate or visually verify that step, leave it explicitly pending.

## 14. Binding energy

For each complex and fragment:

- use the same method and basis;
- use the same solvent model;
- preserve charge and multiplicity bookkeeping;
- state optimized-versus-frozen geometry convention;
- consider counterpoise/BSSE;
- retain all raw energies.

Calculate:

`Delta E = E(complex) - sum(E(fragment_i))`

Do not combine a complex energy from one engine with fragment energies from another engine.

## 15. Failure handling

Read `orca-failures.md`.

Always:

1. preserve the failed `.inp` and `.out`;
2. identify the exact fatal/convergence marker;
3. verify structure, charge, and multiplicity first;
4. change one justified parameter;
5. create a new run case instead of overwriting evidence;
6. parse again and compare.

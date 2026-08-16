# Materials Studio Windows execution runbook

Read completely when the host does not natively load Skills or a job fails.

## 1. Runtime and authorization

Require local filesystem, PowerShell, process control, a user-installed Materials Studio server/scripting environment, and user authorization to use it. A browser chat can prepare files only.

Never attempt license activation, bypass, server modification, or redistribution. A license error is a terminal external-software issue for that run.

## 2. Configure discovery

Pass explicit parameters or configure:

```powershell
$env:MATERIALS_STUDIO_SERVER_ROOT = "<USER_INSTALL_ROOT>"
$env:MATERIALS_STUDIO_RUNNER = "<FULL_PATH_TO_RunMatScript.bat>"
```

Gateway defaults are `localhost:18888` only as a tested convention. Override host/port for the user's authorized installation.

## 3. Preflight

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<MS_SKILL>\scripts\preflight_ms.ps1" `
  -MaterialsStudioRoot "<USER_INSTALL_ROOT>" `
  -RunMatScript "<RUNNER>" `
  -GatewayHost "<HOST>" -GatewayPort <PORT> `
  -OutputJson "<PROJECT>\00_request\ms_preflight.json"
```

Require runner existence and Gateway reachability. This still does not prove a license seat; prove that with the independent smoke script.

## 4. Dedicated run directory

Use `<PROJECT>\03_runs\<case>`. Preserve source copies, manifest, generated Perl, launcher state, `.pl.out`, MatStudio logs, result tables, structures, trajectories, and analysis.

When the installed server mishandles Unicode paths, keep the user-facing project unchanged and let the launcher stage a copy under an ASCII-only temporary directory.

## 5. Smoke test

Copy `assets/ms-script-smoke.pl` to a disposable run directory, then dry-run and execute:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File "<MS_SKILL>\scripts\run_ms_job.ps1" `
  -RunDir "<RUN_DIR>" -ScriptName "ms-script-smoke.pl" `
  -RunMatScript "<RUNNER>" -GatewayHost "<HOST>" -GatewayPort <PORT> -DryRun
```

Remove `-DryRun` after inspecting `ms_job_state.json`. Monitor for `MS_TASK_ALL_DONE`, parse, and require a non-empty log plus the expected generated file.

## 6. Prepare routine jobs

Start from the bundled manifest examples. Validate every structure, component count, force-field assignment, charge, multiplicity, density, ensemble, temperature, pressure, timestep, step count, solvent model, and reference state.

Render routine finite-molecule DMol3 or Forcite jobs with `render_ms_job.py`. For packing or MD, author a manifest-driven independent script using `materialsscript-patterns.md`; do not reuse a confidential project script.

Inspect generated Perl before launch. MaterialsScript property values can differ by release. Probe disputed values on a disposable small case and preserve the error showing allowed values.

## 7. Launch and monitor

Use foreground for short jobs and `-Background` for long jobs. Record project run directory, execution run directory, PID, runner, Gateway, staging state, and exit code.

Do not declare completion because the launcher exited, a process disappeared, or a file exists. Require the expected final marker, no fatal/error markers, all requested result rows, and task-specific convergence.

## 8. Scientific gates

For DMol3 record functional, basis, core treatment, dispersion, solvent, charge, multiplicity, geometry source, SCF convergence, and energy units. Verify density/potential fields before preparing an ESP visualization.

For Forcite/MD verify atom typing and charges, minimization convergence, ensemble sequence, timestep, thermostat/barostat, temperature/pressure/density/volume stability, trajectory frame count, equilibration window, replicas or uncertainty where feasible.

## 9. GUI-only steps

If a display/export operation is unavailable through a verified script API, leave it explicitly pending. A computer-control-capable agent may perform and visually inspect it; a shell-only agent must give exact GUI steps and must not claim an image was exported.

## 10. Failure handling

- Empty `.pl.out`: inspect runner/Gateway mismatch and smoke-test again.
- Unicode path error: use automatic ASCII staging.
- Invalid property value: preserve the log, change one value based on the installed release, and probe again.
- Process exit without marker: treat as incomplete.
- License error: stop, preserve evidence, and ask the user to resolve authorization with the vendor or administrator.

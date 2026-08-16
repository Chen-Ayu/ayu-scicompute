# PySCF execution runbook

## Install

Use an isolated environment and install the versions declared by the repository. Geometry optimization additionally requires geomeTRIC or PyBerny.

## Preflight

```powershell
<PYTHON> scripts/preflight_pyscf.py --output <RUN_DIR>\pyscf_preflight.json
```

Require PySCF import success. Require geomeTRIC only for optimization.

## Prepare

Copy the example manifest and an XYZ file into a dedicated run directory. Confirm atom count, charge, multiplicity, method, basis, memory, threads, and requested cube properties.

## Dry-run and launch

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File scripts\launch_pyscf_job.ps1 `
  -RunDir <RUN_DIR> -Manifest manifest.json -PythonExe <PYTHON> -DryRun
```

Remove `-DryRun` to execute; add `-Background` for a long job. On other platforms call `run_pyscf_job.py` directly.

## Completion

Require a zero exit code, completed state JSON, completed summary JSON, SCF convergence, and any task-specific convergence gate. Output-file existence is insufficient.

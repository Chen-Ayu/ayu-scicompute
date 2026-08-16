# PySCF quality gates

## All jobs

- Require `normal_termination = true`, `scf_converged = true`, and `PYSCF_TASK_COMPLETED` in captured output.
- Preserve manifest, XYZ, checkpoint, stdout, stderr, state JSON, and summary JSON.
- Record PySCF, Python, NumPy, method, basis, charge, multiplicity, and geometry source.
- Keep failed jobs and exception text.

## Optimization and frequency

- Require `optimization_converged = true` before claiming an optimized structure.
- Require an optimized XYZ output.
- For a requested minimum, inspect all harmonic frequencies and report significant imaginary modes.

## Orbitals and MEP

- Report restricted/unrestricted treatment and spin-channel labels.
- Verify cube files exist and are non-empty before promising a visualization.
- Use consistent cube resolution, margin, isodensity, and color scale across comparisons.
- Do not label Mulliken charges or an MEP cube as CHELPG charges.

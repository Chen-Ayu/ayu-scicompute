# ORCA Failure Triage

## SCF failure

1. Preserve the failed input and output.
2. Check charge, multiplicity, geometry, and near-overlapping atoms.
3. Inspect whether the state is open-shell or electronically difficult.
4. Increase iterations or use a documented convergence aid such as SlowConv only when justified.
5. Re-run and record the exact change.

## Optimization failure

- Check whether the maximum cycle count was reached.
- Inspect the last geometry for dissociation, proton transfer, or unphysical contacts.
- Consider a cheaper pre-optimization or a better starting conformer.
- Do not continue to frequency or property reporting on a nonconverged geometry.

## Parallel failure

- Use the full `orca.exe` path.
- Confirm the MS-MPI runtime and helper executables are discoverable.
- Reduce `nprocs` for a diagnostic rerun.
- Keep the ORCA directory on `PATH` during execution.

## Missing property output

- Confirm the required keyword was present.
- Confirm normal termination.
- Use the matching ORCA 6.1 helper program and preserve its command/output.
- Do not substitute a different charge model or orbital plot without labeling it.

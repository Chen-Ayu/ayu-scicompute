# Materials Studio Quality Gates

## All jobs

- Confirm the `.pl.out` log exists and contains the expected final marker.
- Search for `error condition`, `failed`, `cannot load`, `license`, `SCF`, and `not converged`.
- Confirm every requested case appears in a result table.
- Keep failed rows instead of dropping them.

## DMol3

- Confirm SCF convergence and normal engine completion.
- Confirm geometry optimization convergence when an optimized minimum is claimed.
- Record functional, basis, dispersion, core treatment, charge, multiplicity, solvent, and geometry source.
- Confirm density/potential field files exist before preparing ESP visualization.
- Do not mix raw DMol3 energy units with kcal/mol or kJ/mol without an explicit verified conversion.

## Forcite and MD

- Confirm force-field types and charges were assigned to all atoms.
- Confirm minimization did not merely hit the maximum iteration count.
- Inspect temperature, energy, pressure, density, and volume time series.
- Select and record an equilibrated analysis window.
- Check periodic-cell integrity and trajectory frame count.
- Use replicas or uncertainty estimates for comparative MD claims when feasible.

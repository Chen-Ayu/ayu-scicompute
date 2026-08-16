# ORCA Quality Gates

## Normal completion

Require `ORCA TERMINATED NORMALLY` in the output. A generated `.gbw` file alone is not proof of success.

## SCF and orbitals

- Reject outputs with unresolved SCF nonconvergence.
- Confirm the final single-point energy is present.
- Extract frontier orbitals from the final orbital table.
- For unrestricted jobs, report how alpha/beta frontier levels were combined.

## Optimization and frequency

- Require `THE OPTIMIZATION HAS CONVERGED` for an optimized structure.
- Verify the final geometry file exists.
- For a claimed minimum, check for imaginary frequencies after removing translations/rotations and numerical noise.
- Do not report thermochemistry from a failed or partial frequency job.

## ESP

- State whether the result is CHELPG charges, a potential grid, or an ESP mapped on an electron-density surface.
- Preserve the input, output, `.gbw`, and any cube/grid generation commands.
- Use consistent grid and color limits for comparisons.

## Binding and comparisons

- Check charge and multiplicity conservation across the energy cycle.
- Use identical method/basis/solvent settings.
- State whether geometries are optimized independently or frozen from the complex.
- Report units and conversion constants.

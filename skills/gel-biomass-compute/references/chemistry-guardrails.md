# Chemistry guardrails

## Structure and state

- Check elements, coordinates, connectivity where available, hydrogens, formal charge, counterions, and duplicate atoms.
- Treat protonation, counterion removal, radical state, and fragment capping as changes of chemical identity.
- Require a positive integer multiplicity and check electron-count parity where possible.
- Sample flexible lignin, polysaccharide, polymer-fragment, and additive conformations before comparative claims.

## Orbitals and ESP

- Report geometry source, engine version, method, basis, dispersion, solvation, charge, and multiplicity beside orbital energies.
- Label restricted/unrestricted and alpha/beta quantities correctly.
- Distinguish electron density, electrostatic potential, population-analysis charges, CHELPG charges, and mapped ESP surfaces.
- Use consistent grids, isodensity surfaces, and color scales for comparisons.

## Binding energy

Use `Delta E = E(complex) - sum(E(fragment_i))`. Keep engine, method, basis, solvent, charge bookkeeping, and geometry convention consistent. State whether fragments are optimized separately or frozen in complex geometry, and assess BSSE when relevant.

## Reporting

- Preserve raw units and document conversions.
- Never hide a failed case.
- Do not convert finite-cluster evidence into an unsupported bulk-gel conclusion.

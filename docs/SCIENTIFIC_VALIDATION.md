# Scientific validation

## Software validation

- Validate Skill structure and scripts.
- Run engine preflight and a disposable smoke job.
- Test normal, incomplete, failed, and malformed cases.
- Preserve exact versions and raw evidence.

## Scientific validation

- Confirm chemical identity, charge, multiplicity, counterions, and model boundaries.
- Compare selected methods with literature or a higher-level reference where appropriate.
- Verify conformational sensitivity for flexible fragments.
- Keep binding-energy reference states consistent and assess BSSE when relevant.
- Inspect imaginary frequencies for claimed minima.
- For MD, demonstrate equilibration and use uncertainty/replicas where feasible.
- Do not treat finite-fragment descriptors as direct proof of bulk gel performance.
- For transition-metal systems, test relevant oxidation/spin states and assess relativistic and multireference risks.
- For periodic materials, converge pseudopotential/cutoff, k-point mesh, cell/supercell, magnetism and finite-size choices.
- For surfaces, defects and adsorption, document reference energies, slab/vacuum, charge corrections and site sampling.

## Current evidence

The project has historical end-to-end ORCA and Materials Studio runs on the development machine. Public examples contain only synthetic or explicitly approved data. PySCF integration is configured for Linux CI and remains pending until the first private push; native Windows support depends on a suitable distribution or compiler toolchain. Gaussian and VASP are roadmap adapters and have no execution claim in this release.

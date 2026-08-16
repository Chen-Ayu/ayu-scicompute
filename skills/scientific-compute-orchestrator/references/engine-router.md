# Engine router

| Scientific need | Current route | Future/alternative route | Required caution |
|---|---|---|---|
| Finite organic/inorganic molecule SP, orbitals, density, MEP | PySCF | ORCA, Gaussian planned | charge, multiplicity, conformer, solvent and method dependence |
| Transition-metal complex or metal cluster | ORCA or task-reviewed PySCF | Gaussian planned | oxidation/spin states, relativistic effects, multireference risk |
| Molecular optimization/frequency/thermochemistry | PySCF or ORCA | Gaussian planned | minimum requires frequency check; standard states must be explicit |
| Binding/interaction energy | one internally consistent PySCF/ORCA cycle | Gaussian planned | fragment states, deformation, BSSE, solvent and basis consistency |
| Polymer/gel packing and classical MD | Materials Studio with user license | open MD adapter planned | force-field suitability, equilibration, replicas and uncertainty |
| Periodic molecular solid through existing MS workflow | Materials Studio when method is supported | VASP planned | cell, k-points, dispersion and periodic convergence |
| Bulk metal, magnetic solid, surface, defect, adsorption, band/DOS | preparation-only in this release | VASP planned | pseudopotential, cutoff, k-mesh, magnetism, slab/finite-size convergence |
| No lawful engine or no process tools | preparation-only | none | produce files and commands only; never claim execution |

Do not route by brand familiarity alone. Choose an engine only after the system representation, observable, accuracy target, periodicity, license, compute budget and adapter maturity agree.

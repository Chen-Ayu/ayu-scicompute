# Materials Studio Method Router

| Need | Module | Minimum record |
|---|---|---|
| Pack polymer, solvent, ions, or additives | Amorphous Cell | component counts, density target, temperature, periodic box, force field |
| Minimize or screen large organic structures | Forcite | force field, charges, quality, convergence thresholds |
| Anneal or equilibrate | Forcite Dynamics | ensembles, temperature schedule, timestep, thermostat, barostat, steps |
| Production classical MD | Forcite Dynamics | restart source, ensemble, timestep, trajectory frequency, production window |
| Molecular or periodic DFT | DMol3 | charge, multiplicity, functional, basis, core treatment, dispersion, solvent |
| HOMO/LUMO | DMol3 Energy | optimized geometry source, SCF convergence, orbital energies and gap |
| ESP field | DMol3 Energy | On the local x64 Server use `CalculateChargeDensity => "Field"` and `CalculatePotential => "Field"`, then verify fields in the result XSD or exported field files |
| Pair/cluster energy | DMol3 Energy | consistent fragments, complex, geometry convention, method and units |

## Recommended staged preparation

For flexible biomass fragments:

1. validate chemistry and formal charge;
2. perform conformer sampling;
3. optimize selected conformers consistently;
4. run electronic properties on more than one low-energy conformer when conclusions are sensitive.

For gel MD:

1. optimize components;
2. construct the cell at a documented low or target density;
3. minimize the periodic cell;
4. heat or anneal if required;
5. equilibrate density under NPT;
6. run production under the scientifically selected ensemble;
7. analyze only an equilibrated window.

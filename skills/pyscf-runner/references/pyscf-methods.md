# PySCF method guidance

## Presets

- `pbe0-def2-svp`: practical DFT smoke tests and preliminary screening.
- `pbe0-def2-tzvp`: stronger molecular DFT baseline when affordable.
- `b3lyp-def2-svp`: compatibility-oriented screening, not a universal default.
- `hf-def2-svp`: method/debug baseline, not a general materials-chemistry production method.

Every manifest may override method family, XC functional, basis, grid level, SCF tolerance, maximum cycles, density fitting, and solvent dielectric.

## Selection rules

- Add diffuse basis functions for anions or diffuse density when scientifically required.
- Check open-shell states explicitly and inspect spin contamination where applicable.
- Dispersion is not silently added. Record and validate any PySCF dispersion extension separately.
- Use one consistent level for a complex and all fragments in a binding-energy cycle.
- For flexible biomass fragments, sample conformers before expensive DFT and report geometry provenance.
- Use implicit solvent only when its dielectric and cavity approximation match the question; explicit solvent molecules change the chemical model.

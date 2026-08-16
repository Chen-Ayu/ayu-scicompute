# ORCA Method Router

## ORCA version

Detect the installed ORCA version during preflight and preserve the evidence in the project. Verify that every keyword and helper workflow is supported by that version.

## Presets

### `fast-opt`

Use `r2SCAN-3c Opt TightSCF` for efficient finite-molecule geometry preparation and conformer refinement when the elements and model are supported.

### `dft-opt-freq`

Use `PBE0 D4 def2-TZVP def2/J RIJCOSX Opt Freq TightSCF` when a hybrid-DFT optimized minimum and frequencies are required and cost is acceptable.

### `frontier-esp`

Use `PBE0 D4 def2-TZVP def2/J RIJCOSX TightSCF CHELPG` on a defensible geometry for HOMO/LUMO descriptors and CHELPG charges. Add an optimization or consume a previously validated optimized geometry.

These are starting presets, not universal truth. Change them when metal centers, open-shell states, anions, diffuse electron density, heavy elements, multireference character, or literature comparability require it.

## Solvent

Use a documented implicit-solvent keyword only when it represents the experimental question. Keep gas-phase and solution-phase energies separate. Explicit waters or ions change the model and must be recorded as structure components.

## Binding energy

Use one consistent level for the complex and all fragments:

`Delta E = E(complex) - sum(E(fragment_i))`

For atom-centered basis sets, evaluate counterpoise/BSSE when the scientific claim depends on small energy differences. State whether deformation energy and thermal corrections are included.

## Parallel and memory controls

- Set `%pal nprocs` explicitly.
- Set `%maxcore` per process, not total memory.
- Leave memory for Windows and helper processes.
- Reduce cores when the selected method or available memory does not scale safely.

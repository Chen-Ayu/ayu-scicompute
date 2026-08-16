# Validation evidence

This page separates software-chain evidence from scientific claims.

## Public smoke evidence

### ORCA adapter

A real ORCA 6.1.1 water single-point smoke job terminated normally and the parser extracted:

- total energy: `-76.381935997111 Eh`;
- HOMO: `-9.0405 eV`;
- LUMO: `1.5999 eV`;
- frontier gap: `10.6404 eV`;
- dipole magnitude: `2.17715727 D`.

These values validate launch/parsing behavior for that exact smoke setup. They are not benchmark claims and must not be compared directly with another method/engine.

### Materials Studio adapter

A real Materials Studio 23.1 DMol3 water smoke job produced the expected final marker, a complete result row, and parsed frontier values (`HOMO -7.009 eV`, `LUMO 2.155 eV`, `gap 9.164 eV`). The public repository does not distribute vendor outputs or software files.

## Prior private research-case families

Development history includes lignin/lignosulfonate conformer and frontier-orbital work, DMSO/LS and PVA binding workflows, zinc-solvation MD, and additive/solvation-shell trajectory analysis. Those files are intentionally excluded until publication, collaborator, and intellectual-property review is complete.

## PySCF status

The open PySCF backend has a Linux CI integration test covering SCF, frontier orbitals, Mulliken charges, density cube, MEP cube, and HOMO/LUMO cubes. The first remote CI result remains a release gate. Native Windows installation on the development machine failed cleanly because no wheel/compiler toolchain was available; the preflight reports that limitation instead of claiming execution.

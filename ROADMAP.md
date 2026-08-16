# AyuSciCompute roadmap

## 0.3 — general orchestration baseline

- general controller for molecules, metal clusters, polymers and periodic-material task contracts;
- validated ORCA and Materials Studio adapter evidence;
- implemented PySCF path with Linux CI;
- gel/biomass retained as the first specialized domain pack;
- maturity-aware routing, schemas, evaluations, security and release audit.

## 0.4 — Gaussian adapter

- lawful-installation preflight and version detection;
- Link 0/route/charge-multiplicity input model;
- SP, Opt, Freq, thermochemistry, population/ESP and checkpoint workflows;
- termination, SCF, optimization and frequency gates;
- public regression cases and license boundary.

## 0.5 — VASP and periodic materials

- POSCAR/INCAR/KPOINTS/POTCAR-reference contract without distributing POTCAR;
- convergence, relaxation, magnetism and restart gates;
- metals, molecular solids, surfaces, adsorption and defects;
- band structure, DOS/PDOS and selected post-processing;
- scheduler-ready execution and provenance records.

## 0.6 — open MD and analysis

- scientifically reviewed ASE/OpenMM/GROMACS route;
- polymer/gel construction and force-field provenance;
- validated RDF, MSD, hydrogen bonds, density, Rg and uncertainty workflows;
- reproducible public benchmarks.

## 1.0 criteria

- public CI on frozen open-source environments;
- independent molecular and periodic/MD reproductions;
- stable schemas, migration policy and artifact hashing;
- scheduler support and resumable campaigns;
- external scientific review of presets and gates;
- threat-model review and documented limitations.

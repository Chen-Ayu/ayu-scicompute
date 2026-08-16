# Capability maturity

## Current repository baseline

| Adapter | Repository maturity | Evidence boundary |
|---|---|---|
| ORCA | validated adapter | real ORCA 6.1.1 smoke output parsed; task-specific chemistry still requires review |
| Materials Studio | validated adapter | real MS 23.1 DMol3 smoke output parsed; proprietary engine remains user supplied |
| PySCF | implemented adapter | runner, parsers and Linux CI test exist; first remote CI remains a release gate |
| Gel/biomass domain | implemented domain pack | detailed molecular/polymer/MD contracts; not a claim about every gel system |
| Gaussian | planned | no runner in this release; do not claim execution |
| VASP | planned | no runner in this release; do not claim execution or POTCAR access |
| Open classical MD | planned | candidate ecosystems include ASE/OpenMM/GROMACS; select only after method review |

## Claim discipline

Platform scope describes the architecture and roadmap. Current capability describes what this release can actually execute and validate. Keep both visible in every proposal, demo and README.

An engine adapter becoming implemented requires: preflight, manifest/schema, input renderer, safe launcher, monitor, parser, quality gates, failure recovery, license boundary, synthetic example, regression test and one traceable smoke run.

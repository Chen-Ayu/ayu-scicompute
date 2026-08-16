# Security policy and threat model

## Scope

This repository generates files and launches user-selected local scientific executables. It is not a sandbox. Only run manifests, structures and scripts from trusted sources, preferably in an isolated environment and under a non-administrator account.

## Main threats and controls

| Threat | Control in this repository | Residual risk |
|---|---|---|
| Command/argument injection | launchers use direct process APIs; engine filenames are constrained to safe leaf names | external executables and user-authored scripts still have the user's permissions |
| Path traversal/overwrite | launch targets are resolved; installer destinations are checked beneath the selected root; existing Skills require `--force` | a trusted user may intentionally select sensitive output locations |
| Secret or license leakage | release audit scans common token/key patterns, personal paths, forbidden binaries/license files and VASP licensed artifacts | pattern scans cannot prove absence of every secret |
| False scientific completion | engine-specific normal-termination, convergence and observable gates; failed evidence is retained | a converged calculation may still use a scientifically unsuitable model |
| Dependency compromise | minimal dependencies, Dependabot and CodeQL workflows | GitHub Action tags and upstream packages remain supply-chain dependencies |
| Resource exhaustion | positive resource checks and bounded cube grid parameters | legitimate quantum/MD jobs can still consume substantial CPU, memory and disk |

## Public-release checklist

1. Scan the complete Git history, not only the current tree, for secrets and personal paths.
2. Confirm examples are synthetic, published or explicitly approved for release.
3. Exclude raw trajectories, scratch data, proprietary binaries, license files, POTCAR and licensed pseudopotentials.
4. Run `python tools/validate_repository.py`, `python tools/run_evals.py` and the test suite.
5. Inspect generated input before execution and archive raw output after execution.
6. Report vulnerabilities privately to the repository maintainer before opening a public issue.

## Unsupported security claims

This project has not received an independent penetration test. CodeQL and local scans are useful controls, not a security certification.

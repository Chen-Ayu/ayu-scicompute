# Changelog

## 0.3.0-rc1 — 2026-08-16

- rename the platform to AyuSciCompute and broaden its architecture to molecular and materials simulation;
- add `scientific-compute-orchestrator` as the general entry Skill;
- retain gel/biomass as a specialized domain pack rather than the repository boundary;
- surface the real ORCA and Materials Studio validation evidence;
- add maturity-aware routing for molecules, metal clusters, polymers and periodic-material tasks;
- record Gaussian, VASP and open MD as roadmap adapters without claiming current execution;
- update schemas, evaluations, tests, documentation and release naming.

## 0.2.0-rc2 — 2026-08-16

- position the project as an evidence-gated multi-engine research agent;
- add honest related-work comparison, maturity levels and roadmap;
- add machine-readable task and engine-summary schemas plus agent evaluations;
- reject ORCA optimization/frequency jobs that terminate normally without required scientific evidence;
- add charge/multiplicity and cube-resource validation to the PySCF runner;
- constrain launcher filenames and installer destinations;
- distinguish implemented workflows from scientific scaffolds;
- add CodeQL, dependency updates and release packaging tools.

## 0.2.0-rc1 — 2026-08-16

- initial public-release candidate with four Skills and three engine adapters.

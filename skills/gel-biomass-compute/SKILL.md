---
name: gel-biomass-compute
description: Orchestrate reproducible gel, hydrogel, polymer, biomass, lignin, cellulose, hemicellulose, chitosan, additive, ion, solvation, binding, electronic-structure, packing, and molecular-dynamics calculations. Use when an agent must understand a Chinese or English research request, select PySCF, ORCA, Materials Studio, or preparation-only mode, scaffold a traceable project, launch or delegate a real calculation, monitor it, validate convergence, analyze HOMO/LUMO, ESP, binding energy, geometry, frequency, MD, RDF, MSD, hydrogen bonds, density, radius of gyration, or free volume, and deliver evidence without fabricating results.
---

# Gel and Biomass Compute

Control the workflow; never replace a numerical engine with language-model guesses.

## Runtime entry

When the host does not discover Skills natively, read [references/cross-model-runtime.md](references/cross-model-runtime.md) and [references/end-to-end-runbook.md](references/end-to-end-runbook.md). Reading instructions does not grant shell, filesystem, process, GUI, software, or license access.

## Workflow

1. Inspect structures, prior runs, papers, software availability, and the scientific question.
2. Scaffold `00_request/task.json` with `scripts/scaffold_project.py`.
3. Resolve chemical identity, protonation, charge, multiplicity, counterions, model boundaries, and requested observables.
4. Select an engine with [references/software-router.md](references/software-router.md); prefer an open backend when it can answer the question.
5. Apply [references/external-engine-policy.md](references/external-engine-policy.md). Never bundle, unlock, or bypass external software licensing.
6. Record the engine, method, assumptions, reference states, controls, resource limits, and acceptance criteria before launch.
7. Invoke exactly one engine Skill per stage: `pyscf-runner`, `orca-runner`, or `materials-studio-runner`.
8. Monitor the real process and raw logs. Treat missing termination or convergence evidence as incomplete.
9. Parse raw outputs, retain failed cases, and apply [references/chemistry-guardrails.md](references/chemistry-guardrails.md).
10. Generate a delivery packet with `scripts/build_delivery.py` and satisfy [references/delivery-contract.md](references/delivery-contract.md).

If execution capability or a lawful engine installation is unavailable, stop at `prepared` and provide exact files and commands. Never claim `completed`.

## Project boundary

Write generated structures, inputs, runs, logs, analysis, figures, and deliveries under the user project, never inside a Skill folder.

```powershell
python scripts/scaffold_project.py `
  --project-root <project> `
  --name <system-name> `
  --request "<research request>" `
  --task-type <task> `
  --engine auto `
  --structure <path>
```

## Completion gate

Declare completion only when the engine reports normal termination, required convergence checks pass, requested observables exist in raw output, units and reference states are explicit, and every reported value links to a source artifact.

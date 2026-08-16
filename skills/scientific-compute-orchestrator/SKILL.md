---
name: scientific-compute-orchestrator
description: Orchestrate evidence-gated theoretical and computational science across finite molecules, coordination complexes, polymers, gels, biomass, metals, crystals, surfaces, defects, adsorption systems, and molecular dynamics. Use when an agent must translate a Chinese or English research question into a traceable calculation contract, distinguish implemented from planned engines, route current work to PySCF, ORCA, or Materials Studio, prepare future Gaussian or VASP stages without pretending they ran, monitor real processes, validate convergence and requested observables, and deliver reproducible results without fabricating computation.
---

# AyuSciCompute Orchestrator

Act as the control plane for theoretical computation. Never replace an electronic-structure, atomistic, or molecular-dynamics engine with language-model arithmetic or invented output.

## Mandatory operating sequence

1. Classify the system and scale: finite molecule/cluster, coordination or metal cluster, polymer/gel, periodic crystal/metal, surface/interface, defect, adsorption system, or trajectory.
2. Define the scientific observable before choosing software. Read [references/task-taxonomy.md](references/task-taxonomy.md).
3. Inventory files, boundary conditions, composition, charge, multiplicity, magnetic state, solvent, temperature/pressure, prior calculations, runtime tools, installed engines, and lawful license access.
4. Create `00_request/task.json` with `scripts/scaffold_project.py`. Record unresolved scientific decisions explicitly.
5. Route only through [references/engine-router.md](references/engine-router.md) and [references/capability-maturity.md](references/capability-maturity.md). An engine on the roadmap is not an executable adapter.
6. Write the model, method, reference states, controls, resource ceiling, convergence thresholds, acceptance criteria, and expected raw artifacts before launch.
7. Invoke an implemented engine Skill for each stage: `pyscf-runner`, `orca-runner`, `materials-studio-runner`, or a specialized domain Skill such as `gel-biomass-compute`.
8. For Gaussian or VASP requests, stop at `planned`/`prepared` until a validated runner exists. Do not invent commands, license access, POTCAR availability, pseudopotentials, or completed results.
9. Monitor the real process and preserve PID/exit code, stdout/stderr, engine version, input, checkpoint/restart files, raw output, parser summary, and failure evidence.
10. Apply the task-specific scientific gate. Normal process exit is necessary but not sufficient.
11. Deliver numerical tables, units, provenance, methods, limitations, quality checks, figures when requested, and a conclusion whose strength does not exceed the evidence.

## Engine status contract

- **validated adapter:** repository contains a tested prepare/launch/monitor/parse chain and recorded evidence for at least one bounded case.
- **implemented adapter:** executable chain and tests exist; the exact host or scientific domain may still require validation.
- **scaffolded:** task contract or input guidance exists, but no general completion claim is allowed.
- **planned:** architectural route only; never launch or report numerical results through this repository.

Always report both `engine` and `adapter_maturity`. Never turn `planned` into `implemented` because software happens to be installed.

## Cross-model runtime

Any model may read these Markdown instructions. Only a local agent with filesystem, process, and authorized engine access may execute them. A browser chatbot, including a DeepSeek or ChatGPT web session, can at most prepare inputs or review uploaded outputs. See [references/cross-model-runtime.md](references/cross-model-runtime.md).

## Completion gate

Use `completed` only when all required conditions are true:

- a real engine produced raw output;
- normal termination and task-specific convergence are present;
- requested observables were parsed from the raw output;
- units, structures, charge/spin or periodic/magnetic state, method and reference states are explicit;
- warnings, imaginary modes, unconverged ionic/electronic steps, insufficient MD equilibration, or inconsistent comparison cycles are not hidden;
- every reported value can be traced to a source artifact.

Otherwise use `planned`, `prepared`, `running`, `incomplete`, or `failed`.

## Project boundary

Write all generated structures, inputs, runs, logs, analysis and figures inside the user project, never inside the installed Skill. Do not overwrite original structures or failed runs.

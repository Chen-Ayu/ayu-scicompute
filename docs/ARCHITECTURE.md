# Architecture

## Platform layers

1. **Question layer:** natural-language scientific objective and supplied evidence.
2. **Scientific contract:** system class, observable, model, boundary conditions, reference states, controls and acceptance criteria.
3. **Maturity-aware router:** engine capability, adapter readiness, license, runtime and compute budget.
4. **Domain packs:** specialized protocols for gels/biomass today and additional domains later.
5. **Engine adapters:** preflight, manifest, renderer, launcher, monitor, parser, recovery and quality gates.
6. **Evidence ledger:** input, version, command, PID/exit code, logs, checkpoints, raw output, summary and hashes.
7. **Scientific acceptance:** electronic/ionic convergence, requested observable, units, reference consistency and task-specific diagnostics.
8. **Delivery:** data tables, methods, limitations, figures, conclusions and file index.

## Trust states

`planned → prepared → running → executed → validated → reproduced`

Any state may move to `incomplete` or `failed`. `executed` means a real process produced output; `validated` additionally requires scientific gates. Roadmap engines remain `planned` even if their names appear in a task contract.

## Extension contract

Every new engine adapter must provide: license boundary, capability declaration, preflight, version capture, schema/manifest, safe input renderer, safe launcher, monitor, parser, quality gates, recovery guide, public examples, regression tests and a traceable smoke run.

The controller must not absorb vendor-specific commands. It selects an adapter and verifies its contract.

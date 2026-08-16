# End-to-end runbook

1. Classify runtime as execution-capable, file-only, or chat-only.
2. Create the project tree and task contract.
3. Validate structures and electronic states.
4. Run engine preflights and capture their JSON output.
5. Route one stage at a time and record the decision.
6. Render and inspect input before launch.
7. Dry-run launchers when available.
8. Launch in a dedicated run directory; preserve PID, exit code, stdout, stderr, and state JSON.
9. Monitor normal-termination and convergence markers.
10. Parse raw outputs to an engine summary.
11. Apply scientific quality gates and compare only consistent cases.
12. Build delivery files and label limitations.

Use `planned`, `prepared`, `running`, `completed`, `failed`, or `incomplete`. Output-file existence alone never proves completion.

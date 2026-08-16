# Cross-model runtime contract

## Local execution agent

May run the workflow only when it can read/write files, launch and inspect processes, access the authorized engine, wait for jobs, and preserve raw evidence. Codex, Claude Code, OpenCode or a locally tooled DeepSeek model can qualify.

## File-only agent

May create contracts, manifests and inputs and may parse output supplied later. It must use `prepared` until raw engine output exists.

## Web chat

May explain methods or review uploaded text. It cannot claim access to local executables, licenses, queues, PIDs, logs or results.

## Handoff record

Every model-to-model or person-to-agent handoff must include the task contract path, engine and adapter maturity, current state, exact working directory, completed stages, unresolved decisions, last raw log, next command and acceptance criteria.

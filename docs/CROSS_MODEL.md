# Cross-model operation

The Skills are Markdown plus Python/PowerShell/Perl. A model can understand them without native Skill discovery by reading the files in the documented order.

Execution depends on host tools:

- local filesystem and shell: full workflow if an engine is available;
- filesystem without process execution: prepare and parse only;
- browser chat: review uploaded text only.

DeepSeek, Claude, Codex, or another model must not claim local execution without showing the executable/interpreter, run directory, command, PID/exit code, raw output, normal-termination marker, and parser summary.

# Cross-model runtime contract

This repository is plain Markdown plus PowerShell and Python scripts. Any capable model can read it; only a local tool-enabled agent can execute it.

## Level A: local execution agent

Require all of the following:

- read and write local files;
- run PowerShell and Python;
- start and inspect external processes;
- access the user-installed engine and project directory;
- wait for long jobs and re-read logs.

Run the complete workflow only at Level A.

## Level B: file agent without process execution

Prepare structures, manifests, input files, and exact launch commands. Never state that the engine ran. Parse returned output only after it is present and readable.

## Level C: web chat

Explain or review uploaded text only. Do not claim access to the user's computer, executable, PID, logs, or results.

## Evidence required before `completed`

Require the executable path, working directory, input filename, exit code or PID, engine normal-termination marker, raw output path, and parser summary. Otherwise use `planned`, `prepared`, `running`, `failed`, or `incomplete`.

## DeepSeek and other models

The model brand is not decisive. A local DeepSeek-based agent with shell and file tools can follow these instructions. A browser chat cannot launch a desktop or command-line program merely because it has read the Skill.

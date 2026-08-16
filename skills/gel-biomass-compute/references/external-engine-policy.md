# External engine policy

The repository publishes independent workflow code and interoperability adapters.

- PySCF is the default open-source molecular backend.
- ORCA and Materials Studio are optional external backends installed and licensed by the user.
- Never distribute external executables, installers, manuals, license files, license-server settings, or vendor sample assets.
- Never bypass authentication, license checks, activation, seat limits, or server controls.
- Detect availability; do not assume entitlement from an executable path.
- Record engine name and version in every run.
- If the user cannot confirm authorization, prepare inputs only or route to an open backend that supports the task.

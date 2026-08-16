# Water frontier-orbital smoke example

This synthetic small-molecule example tests input rendering and launcher preparation. It is not a scientific validation case for gels or biomass.

1. Copy `manifest.json` and `water.xyz` to a disposable run directory.
2. Render the input with `skills/orca-runner/scripts/render_orca_input.py`.
3. Run the launcher with `-DryRun` first.
4. Execute only after confirming the local ORCA license and executable path.
5. Require `ORCA TERMINATED NORMALLY` and parse the output before reporting values.

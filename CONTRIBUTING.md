# Contributing

Contributions must preserve scientific traceability and external-license boundaries.

1. Create a focused branch and explain the scientific use case.
2. Add or update an engine manifest, quality gate, and test when behavior changes.
3. Keep private structures, credentials, binaries, license files, and large outputs out of Git.
4. Never weaken completion gates merely to make a test pass.
5. Document method assumptions and failure behavior.
6. Run `python tools/validate_repository.py` before opening a pull request.

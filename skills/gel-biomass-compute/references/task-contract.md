# Task contract

`00_request/task.json` is the authority for one calculation campaign.

Required fields:

```json
{
  "schema_version": "1.0",
  "project_name": "example",
  "request": "calculate HOMO LUMO and ESP",
  "task_type": "homo-lumo",
  "engine": "orca",
  "status": "planned",
  "structures": [{"path": "01_structures/example.xyz", "role": "target"}],
  "chemistry": {"charge": 0, "multiplicity": 1, "solvent": null},
  "method": {},
  "controls": [],
  "deliverables": ["result_table", "raw_outputs", "method_summary"]
}
```

Allowed tasks: `geometry-opt`, `frequency`, `homo-lumo`, `esp`, `binding-energy`, `conformer-search`, `amorphous-cell`, `md`, `rdf`, `msd`, `hbond`, `density`, `radius-of-gyration`, and `free-volume`.

Use only `planned -> prepared -> running -> completed` or transition to `failed`/`incomplete`. Process exit alone is not completion.

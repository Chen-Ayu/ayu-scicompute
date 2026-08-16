#!/usr/bin/env python3
"""Create a traceable gel/biomass computation project without running an engine."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


TASKS = {
    "geometry-opt",
    "frequency",
    "homo-lumo",
    "esp",
    "binding-energy",
    "conformer-search",
    "amorphous-cell",
    "md",
    "rdf",
    "msd",
    "hbond",
    "density",
    "radius-of-gyration",
    "free-volume",
}


def route(task_type: str) -> str:
    if task_type in {
        "amorphous-cell",
        "md",
        "rdf",
        "msd",
        "hbond",
        "density",
        "radius-of-gyration",
        "free-volume",
        "conformer-search",
    }:
        return "materials-studio"
    return "pyscf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--task-type", required=True, choices=sorted(TASKS))
    parser.add_argument(
        "--engine",
        default="auto",
        choices=["auto", "pyscf", "orca", "materials-studio", "prepared-only"],
    )
    parser.add_argument("--structure", action="append", default=[])
    parser.add_argument("--charge", type=int)
    parser.add_argument("--multiplicity", type=int)
    parser.add_argument("--solvent")
    parser.add_argument("--copy-structures", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.multiplicity is not None and args.multiplicity < 1:
        raise SystemExit("multiplicity must be a positive integer")

    root = Path(args.project_root).expanduser().resolve()
    task_path = root / "00_request" / "task.json"
    if task_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing task: {task_path}")

    directories = [
        "00_request",
        "01_structures",
        "02_inputs",
        "03_runs",
        "04_logs",
        "05_analysis",
        "06_figures",
        "07_delivery",
    ]
    for directory in directories:
        (root / directory).mkdir(parents=True, exist_ok=True)

    structures = []
    for item in args.structure:
        source = Path(item).expanduser().resolve()
        record = {"source_path": str(source), "role": "target"}
        if source.exists() and args.copy_structures:
            destination = root / "01_structures" / source.name
            if destination.exists() and destination.resolve() != source:
                raise SystemExit(f"Structure destination already exists: {destination}")
            if destination.resolve() != source:
                shutil.copy2(source, destination)
            record["path"] = str(destination.relative_to(root))
        else:
            record["path"] = str(source)
            record["exists"] = source.exists()
        structures.append(record)

    selected_engine = route(args.task_type) if args.engine == "auto" else args.engine
    chemistry = {
        "charge": args.charge,
        "multiplicity": args.multiplicity,
        "solvent": args.solvent,
    }
    unresolved = [
        key for key in ("charge", "multiplicity") if chemistry[key] is None
    ]
    if selected_engine == "undecided":
        unresolved.append("engine")

    task = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_name": args.name,
        "request": args.request,
        "task_type": args.task_type,
        "engine": selected_engine,
        "status": "planned",
        "structures": structures,
        "chemistry": chemistry,
        "method": {},
        "controls": [],
        "deliverables": [
            "result_table",
            "raw_outputs",
            "method_summary",
            "chinese_conclusion",
        ],
        "unresolved": unresolved,
    }
    task_path.write_text(
        json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    method_decision = root / "00_request" / "method_decision.md"
    method_decision.write_text(
        "# Method decision\n\n"
        f"- Scientific request: {args.request}\n"
        f"- Task type: {args.task_type}\n"
        f"- Initial engine route: {selected_engine}\n"
        f"- Unresolved before launch: {', '.join(unresolved) or 'none'}\n"
        "- Model choice:\n"
        "- Method and controls:\n"
        "- Expected outputs:\n"
        "- Known limitations:\n",
        encoding="utf-8",
    )

    state = {
        "status": "planned",
        "engine": selected_engine,
        "task_file": str(task_path),
        "unresolved": unresolved,
    }
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

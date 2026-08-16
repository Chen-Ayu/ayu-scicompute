#!/usr/bin/env python3
"""Create a general, evidence-gated theoretical-computation project contract."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

MOLECULAR_TASKS = {"single-point", "geometry-opt", "frequency", "homo-lumo", "esp", "binding-energy", "conformer-search"}
MD_TASKS = {"amorphous-cell", "md", "rdf", "msd", "hbond", "density", "radius-of-gyration", "free-volume"}
PERIODIC_TASKS = {"periodic-relax", "band-structure", "dos", "phonon", "elastic", "surface", "adsorption", "defect", "neb", "magnetic-order"}
TASKS = MOLECULAR_TASKS | MD_TASKS | PERIODIC_TASKS
IMPLEMENTED = {"pyscf", "orca", "materials-studio"}
PLANNED = {"gaussian", "vasp"}


def auto_route(task: str) -> tuple[str, str, list[str], str]:
    if task in MOLECULAR_TASKS:
        return "pyscf", "implemented", ["orca", "gaussian"], "finite molecular open-first route"
    if task in MD_TASKS:
        return "materials-studio", "validated", ["open-md"], "polymer/MD route; user license required"
    return "prepared-only", "planned", ["vasp", "materials-studio"], "periodic/metal adapter roadmap; no VASP runner in this release"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--task-type", required=True, choices=sorted(TASKS))
    parser.add_argument("--domain", default="auto", choices=["auto", "molecular", "metal-cluster", "periodic-material", "polymer-md", "gel-biomass"])
    parser.add_argument("--engine", default="auto", choices=["auto", "pyscf", "orca", "materials-studio", "gaussian", "vasp", "prepared-only"])
    parser.add_argument("--structure", action="append", default=[])
    parser.add_argument("--charge", type=int)
    parser.add_argument("--multiplicity", type=int)
    parser.add_argument("--periodic", action="store_true")
    parser.add_argument("--copy-structures", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.multiplicity is not None and args.multiplicity < 1:
        raise SystemExit("multiplicity must be positive")
    root = Path(args.project_root).expanduser().resolve()
    task_path = root / "00_request" / "task.json"
    if task_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing task: {task_path}")
    for folder in ("00_request", "01_structures", "02_inputs", "03_runs", "04_logs", "05_analysis", "06_figures", "07_delivery"):
        (root / folder).mkdir(parents=True, exist_ok=True)

    structures = []
    for value in args.structure:
        source = Path(value).expanduser().resolve()
        record = {"source_path": str(source), "role": "target", "exists": source.exists()}
        if source.exists() and args.copy_structures:
            destination = root / "01_structures" / source.name
            if destination.exists() and destination.resolve() != source:
                raise SystemExit(f"Structure destination already exists: {destination}")
            if destination.resolve() != source:
                shutil.copy2(source, destination)
            record["path"] = str(destination.relative_to(root))
        else:
            record["path"] = str(source)
        structures.append(record)

    auto_engine, auto_maturity, alternatives, rationale = auto_route(args.task_type)
    domain = args.domain
    if domain == "auto":
        domain = "molecular" if args.task_type in MOLECULAR_TASKS else (
            "polymer-md" if args.task_type in MD_TASKS else "periodic-material"
        )
    engine = auto_engine if args.engine == "auto" else args.engine
    maturity = auto_maturity if args.engine == "auto" else (
        "implemented" if engine in IMPLEMENTED else "planned" if engine in PLANNED else "prepared-only"
    )
    status = "planned"
    unresolved = []
    if not structures:
        unresolved.append("structure")
    if args.task_type in MOLECULAR_TASKS:
        if args.charge is None: unresolved.append("charge")
        if args.multiplicity is None: unresolved.append("multiplicity")
    if engine in PLANNED:
        unresolved.append(f"{engine}-adapter-not-implemented")
    if engine == "prepared-only" and args.task_type in PERIODIC_TASKS:
        unresolved.append("validated-periodic-engine-adapter")

    contract = {
        "schema_version": "2.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "platform": "AyuSciCompute",
        "project_name": args.name,
        "request": args.request,
        "domain": domain,
        "task_type": args.task_type,
        "periodic": bool(args.periodic or args.task_type in PERIODIC_TASKS),
        "engine": engine,
        "adapter_maturity": maturity,
        "alternative_engines": alternatives,
        "route_rationale": rationale,
        "status": status,
        "structures": structures,
        "chemistry": {"charge": args.charge, "multiplicity": args.multiplicity},
        "method": {},
        "boundary_conditions": {},
        "controls": [],
        "acceptance_criteria": [],
        "deliverables": ["raw_outputs", "result_table", "method_summary", "quality_report", "chinese_conclusion"],
        "unresolved": unresolved,
    }
    task_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "00_request" / "method_decision.md").write_text(
        "# Method decision\n\n"
        f"- Request: {args.request}\n- Domain: {domain}\n- Task: {args.task_type}\n"
        f"- Route: {engine} ({maturity})\n- Rationale: {rationale}\n"
        f"- Unresolved: {', '.join(unresolved) or 'none'}\n\n"
        "## Required review\n\n- System representation and boundary conditions:\n- Method and reference states:\n"
        "- Convergence and controls:\n- Expected raw artifacts:\n- Acceptance criteria:\n- Known limitations:\n",
        encoding="utf-8",
    )
    print(json.dumps({"project_root": str(root), "engine": engine, "adapter_maturity": maturity, "status": status, "unresolved": unresolved}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

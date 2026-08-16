#!/usr/bin/env python3
"""Summarize PySCF state without treating file existence as success."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--run-dir", required=True); parser.add_argument("--output")
    args = parser.parse_args(); run_dir = Path(args.run_dir).resolve()
    state_path = run_dir / "pyscf_job_state.json"; summary_path = run_dir / "pyscf_summary.json"
    state = json.loads(state_path.read_text(encoding="utf-8-sig")) if state_path.exists() else {}
    summary = json.loads(summary_path.read_text(encoding="utf-8-sig")) if summary_path.exists() else {}
    completed = summary.get("status") == "completed" and summary.get("normal_termination") and summary.get("scf_converged")
    status = "completed" if completed else summary.get("status") or state.get("status") or "not-started"
    record = {"engine": "pyscf", "run_dir": str(run_dir), "status": status, "state": state, "summary": summary}
    text = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if args.output: Path(args.output).write_text(text, encoding="utf-8")
    print(text, end=""); return 0 if completed else 2


if __name__ == "__main__": raise SystemExit(main())

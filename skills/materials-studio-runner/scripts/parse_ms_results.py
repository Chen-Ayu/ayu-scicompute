#!/usr/bin/env python3
"""Summarize a Materials Studio run directory without inventing missing values."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ERROR_TERMS = (
    "error condition",
    "cannot load",
    "license",
    "not converged",
    "failed",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--output")
    parser.add_argument("--expected-marker", default="MS_TASK_ALL_DONE")
    args = parser.parse_args()
    run_dir = Path(args.run_dir).resolve()
    scan_dir = run_dir
    state_path = run_dir / "ms_job_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        candidate = state.get("execution_run_dir")
        if candidate and Path(candidate).exists():
            candidate_path = Path(candidate)
            if list(candidate_path.glob("*.pl.out")) or (candidate_path / "ms_results.csv").exists():
                scan_dir = candidate_path
    log_paths = sorted(scan_dir.glob("*.pl.out"))
    log_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace") for path in log_paths
    )
    result_path = scan_dir / "ms_results.csv"
    rows = []
    if result_path.exists():
        with result_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    failed_rows = [
        row for row in rows if row.get("status", "").strip().lower() not in {"ok", "completed"}
    ]
    error_hits = [term for term in ERROR_TERMS if term in log_text.lower()]
    marker_found = args.expected_marker in log_text
    status = (
        "completed"
        if marker_found and not error_hits and not failed_rows and rows
        else "incomplete-or-failed"
    )
    summary = {
        "engine": "materials-studio",
        "run_dir": str(run_dir),
        "execution_run_dir": str(scan_dir),
        "status": status,
        "scientific_gate_passed": status == "completed",
        "marker_found": marker_found,
        "error_hits": error_hits,
        "logs": [str(path) for path in log_paths],
        "results_file": str(result_path) if result_path.exists() else None,
        "result_rows": rows,
        "failed_row_count": len(failed_rows),
    }
    output = Path(args.output) if args.output else run_dir / "ms_summary.json"
    output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

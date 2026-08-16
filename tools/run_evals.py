#!/usr/bin/env python3
"""Run deterministic routing and scientific-gate evaluations."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], expected: int | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    if expected is not None and result.returncode != expected:
        raise RuntimeError(result.stdout + result.stderr)
    return result


def main() -> int:
    suite = json.loads((ROOT / "evals" / "eval_cases.json").read_text(encoding="utf-8"))
    passed = 0
    failures = []
    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        water = temp / "water.xyz"
        water.write_text("3\nwater\nO 0 0 0\nH 0 0 1\nH 1 0 0\n", encoding="utf-8")
        for case in suite["cases"]:
            try:
                if case["kind"] == "route":
                    project = temp / case["id"]
                    run([
                        sys.executable,
                        str(ROOT / "skills" / "scientific-compute-orchestrator" / "scripts" / "scaffold_project.py"),
                        "--project-root", str(project), "--name", case["id"],
                        "--request", case["id"], "--task-type", case["task_type"],
                        "--engine", "auto", "--structure", str(water),
                        "--charge", "0", "--multiplicity", "1",
                    ], expected=0)
                    task = json.loads((project / "00_request" / "task.json").read_text(encoding="utf-8"))
                    if task["engine"] != case["expected_engine"]:
                        raise AssertionError(f"got {task['engine']}")
                    if task["adapter_maturity"] != case["expected_maturity"]:
                        raise AssertionError(f"got maturity {task['adapter_maturity']}")
                elif case["kind"] == "orca-output":
                    output = temp / f"{case['id']}.out"
                    summary = temp / f"{case['id']}.json"
                    output.write_text(case["text"], encoding="utf-8")
                    result = run([
                        sys.executable,
                        str(ROOT / "skills" / "orca-runner" / "scripts" / "parse_orca_output.py"),
                        "--output-file", str(output), "--summary", str(summary),
                    ])
                    parsed = json.loads(summary.read_text(encoding="utf-8"))
                    if parsed["status"] != case["expected_status"]:
                        raise AssertionError(f"got {parsed['status']}")
                    expected_return = 0 if case["expected_status"] == "completed" else 2
                    if result.returncode != expected_return:
                        raise AssertionError(f"unexpected return code {result.returncode}")
                else:
                    raise ValueError(f"unknown case kind: {case['kind']}")
                passed += 1
            except Exception as exc:
                failures.append(f"{case['id']}: {exc}")
    if failures:
        print("EVALUATIONS FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 2
    print(f"EVALUATIONS PASSED: {passed}/{len(suite['cases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

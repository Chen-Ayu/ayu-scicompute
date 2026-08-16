#!/usr/bin/env python3
"""Build a conservative delivery packet from a task contract and engine summary."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def flatten_results(summary: dict) -> list[dict]:
    engine = summary.get("engine")
    if engine == "materials-studio":
        return [{"engine": engine, **row} for row in summary.get("result_rows", [])]
    if engine not in {"orca", "pyscf"}:
        return []
    keys = [
        "final_single_point_energy_hartree",
        "homo_ev",
        "lumo_ev",
        "gap_ev",
        "dipole_debye",
        "frequency_count",
    ]
    return [{
        "engine": engine,
        "name": summary.get("name") or Path(summary.get("output_file", engine)).stem,
        "stage": engine,
        **{key: summary.get(key) for key in keys},
        "status": summary.get("status"),
    }]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--engine-summary", required=True)
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    summary_path = Path(args.engine_summary).resolve()
    summary = load_json(summary_path)
    task_path = root / "00_request" / "task.json"
    task = load_json(task_path) if task_path.exists() else {}

    analysis = root / "05_analysis"
    delivery = root / "07_delivery"
    analysis.mkdir(parents=True, exist_ok=True)
    delivery.mkdir(parents=True, exist_ok=True)

    status = summary.get("status", "unknown")
    normal = summary.get("normal_termination", summary.get("marker_found"))
    scientific_gate = summary.get("scientific_gate_passed")
    if scientific_gate is None:
        scientific_gate = status == "completed" and bool(normal)
    run_status = [{
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "engine": summary.get("engine", task.get("engine", "unknown")),
        "status": status,
        "normal_termination": summary.get("normal_termination", summary.get("marker_found")),
        "scientific_gate_passed": scientific_gate,
        "summary_file": str(summary_path),
    }]
    write_csv(
        analysis / "run_status.csv",
        run_status,
        ["checked_at", "engine", "status", "normal_termination", "scientific_gate_passed", "summary_file"],
    )

    rows = flatten_results(summary)
    result_fields = sorted({key for row in rows for key in row}) if rows else [
        "engine", "name", "stage", "status"
    ]
    write_csv(analysis / "results.csv", rows, result_fields)

    quality_notes = list(summary.get("quality_notes", []))
    if summary.get("engine") not in {"pyscf", "orca", "materials-studio"}:
        quality_notes.append("Unsupported engine summary; no numerical rows exported.")
    if status != "completed":
        quality_notes.append("Engine summary is not completed; results are not final.")
    if not scientific_gate:
        quality_notes.append("Scientific acceptance gate did not pass; do not publish numerical claims as validated results.")
    (analysis / "quality_checks.md").write_text(
        "# Quality checks\n\n"
        f"- Engine status: `{status}`\n"
        f"- Raw summary: `{summary_path}`\n"
        + "".join(f"- {note}\n" for note in quality_notes)
        + ("- No additional parser warnings.\n" if not quality_notes else ""),
        encoding="utf-8",
    )

    chemistry = task.get("chemistry", {})
    (delivery / "methods.md").write_text(
        "# Methods\n\n"
        f"- Request: {task.get('request', 'not recorded')}\n"
        f"- Task type: {task.get('task_type', 'not recorded')}\n"
        f"- Engine: {summary.get('engine', task.get('engine', 'unknown'))}\n"
        f"- Charge: {chemistry.get('charge', 'not recorded')}\n"
        f"- Multiplicity: {chemistry.get('multiplicity', 'not recorded')}\n"
        f"- Solvent: {chemistry.get('solvent', 'not recorded')}\n"
        f"- Engine summary: `{summary_path}`\n\n"
        "Review the engine input and method-decision file before publication use.\n",
        encoding="utf-8",
    )

    lines = [
        "# 中文结论",
        "",
        f"- 任务：{task.get('request', '未记录')}",
        f"- 实际计算软件：{summary.get('engine', task.get('engine', '未知'))}",
        f"- 运行状态：{status}",
    ]
    if rows:
        lines.append("- 主要数值已写入 `05_analysis/results.csv`。")
    if status == "completed" and normal and scientific_gate:
        lines.append("- 解析器检测到正常完成标志；仍需结合方法与体系进行科学复核。")
    else:
        lines.append("- 当前结果未通过完整完成门槛，不能作为最终科研结论。")
    lines.extend([
        "- 结构、电荷、自旋、参考态和方法局限见 `methods.md` 与原始输入输出。",
        "",
    ])
    (delivery / "conclusions_zh.md").write_text("\n".join(lines), encoding="utf-8")

    indexed = []
    for folder in (
        "00_request", "02_inputs", "03_runs", "04_logs",
        "05_analysis", "06_figures", "07_delivery",
    ):
        base = root / folder
        if base.exists():
            for path in sorted(item for item in base.rglob("*") if item.is_file()):
                indexed.append({
                    "relative_path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                })
    write_csv(delivery / "file_index.csv", indexed, ["relative_path", "bytes"])
    print(json.dumps({
        "project_root": str(root),
        "status": status,
        "results": str(analysis / "results.csv"),
        "delivery": str(delivery),
        "file_count": len(indexed),
    }, ensure_ascii=False, indent=2))
    return 0 if status == "completed" and normal and scientific_gate else 2


if __name__ == "__main__":
    raise SystemExit(main())

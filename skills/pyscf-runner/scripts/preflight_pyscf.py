#!/usr/bin/env python3
"""Report whether the selected Python environment can run PySCF workflows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def version(name: str) -> str | None:
    try:
        module = __import__(name)
        return getattr(module, "__version__", "installed")
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    record = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "pyscf_version": version("pyscf"),
        "numpy_version": version("numpy"),
        "geometric_available": importlib.util.find_spec("geometric") is not None,
        "berny_available": importlib.util.find_spec("berny") is not None,
    }
    record["ready_for_single_point"] = record["pyscf_version"] is not None
    record["ready_for_geometry_optimization"] = record["ready_for_single_point"] and (
        record["geometric_available"] or record["berny_available"]
    )
    text = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if record["ready_for_single_point"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

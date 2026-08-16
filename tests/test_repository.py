from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(unittest.TestCase):
    def run_python(self, script: Path, *args: str, expected: int = 0):
        result = subprocess.run([sys.executable, str(script), *map(str, args)], text=True, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_release_audit(self):
        self.run_python(ROOT / "tools" / "validate_repository.py")

    def test_controller_routes_open_and_periodic_tasks(self):
        script = ROOT / "skills" / "gel-biomass-compute" / "scripts" / "scaffold_project.py"
        with tempfile.TemporaryDirectory() as temp:
            water = Path(temp) / "water.xyz"; water.write_text("3\nwater\nO 0 0 0\nH 0 0 1\nH 1 0 0\n", encoding="utf-8")
            for task, expected_engine in (("homo-lumo", "pyscf"), ("md", "materials-studio")):
                project = Path(temp) / task
                self.run_python(script, "--project-root", project, "--name", task, "--request", task,
                                "--task-type", task, "--engine", "auto", "--structure", water,
                                "--charge", "0", "--multiplicity", "1")
                contract = json.loads((project / "00_request" / "task.json").read_text(encoding="utf-8"))
                self.assertEqual(contract["engine"], expected_engine)

    def test_orca_and_ms_renderers(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            orca_example = ROOT / "examples" / "orca-water-frontier"
            self.run_python(ROOT / "skills" / "orca-runner" / "scripts" / "render_orca_input.py",
                            "--manifest", orca_example / "manifest.json", "--output", temp / "water.inp")
            self.assertIn("* xyz 0 1", (temp / "water.inp").read_text(encoding="utf-8"))
            ms_manifest = ROOT / "examples" / "ms-dmol3-prepared" / "manifest.json"
            self.run_python(ROOT / "skills" / "materials-studio-runner" / "scripts" / "render_ms_job.py",
                            "--manifest", ms_manifest, "--output", temp / "job.pl")
            self.assertIn("MS_TASK_ALL_DONE", (temp / "job.pl").read_text(encoding="utf-8"))

    def test_general_orchestrator_separates_current_and_roadmap_engines(self):
        script = ROOT / "skills" / "scientific-compute-orchestrator" / "scripts" / "scaffold_project.py"
        with tempfile.TemporaryDirectory() as temp:
            water = Path(temp) / "water.xyz"
            water.write_text("3\nwater\nO 0 0 0\nH 0 0 1\nH 1 0 0\n", encoding="utf-8")
            cases = (
                ("homo-lumo", "pyscf", "implemented"),
                ("md", "materials-studio", "validated"),
                ("band-structure", "prepared-only", "planned"),
            )
            for task, engine, maturity in cases:
                project = Path(temp) / f"general-{task}"
                self.run_python(script, "--project-root", project, "--name", task,
                                "--request", task, "--task-type", task, "--engine", "auto",
                                "--structure", water, "--charge", "0", "--multiplicity", "1")
                contract = json.loads((project / "00_request" / "task.json").read_text(encoding="utf-8"))
                self.assertEqual(contract["engine"], engine)
                self.assertEqual(contract["adapter_maturity"], maturity)
            self.assertIn("validated-periodic-engine-adapter", contract["unresolved"])

    def test_orca_parser_rejects_normal_but_unconverged_optimization(self):
        parser = ROOT / "skills" / "orca-runner" / "scripts" / "parse_orca_output.py"
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            output = temp / "not-converged.out"
            output.write_text(
                "! PBE0 Opt TightSCF\nFINAL SINGLE POINT ENERGY -75.0\n"
                "ORCA TERMINATED NORMALLY\n",
                encoding="utf-8",
            )
            summary_path = temp / "summary.json"
            self.run_python(parser, "--output-file", output, "--summary", summary_path, expected=2)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "incomplete-or-failed")
            self.assertFalse(summary["scientific_gate_passed"])

    def test_orca_parser_rejects_frequency_task_without_frequency_table(self):
        parser = ROOT / "skills" / "orca-runner" / "scripts" / "parse_orca_output.py"
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            output = temp / "missing-freq.out"
            output.write_text(
                "! PBE0 Freq TightSCF\nFINAL SINGLE POINT ENERGY -75.0\n"
                "ORCA TERMINATED NORMALLY\n",
                encoding="utf-8",
            )
            summary_path = temp / "summary.json"
            self.run_python(parser, "--output-file", output, "--summary", summary_path, expected=2)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertFalse(summary["scientific_gate_passed"])

    def test_ms_parser_falls_back_from_empty_staging_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            run_dir = Path(temp) / "run"; staging = Path(temp) / "empty-stage"
            run_dir.mkdir(); staging.mkdir()
            (run_dir / "ms_job_state.json").write_text(json.dumps({"execution_run_dir": str(staging)}), encoding="utf-8")
            (run_dir / "case.pl.out").write_text("MS_TASK_START\nMS_TASK_ALL_DONE\n", encoding="utf-8")
            (run_dir / "ms_results.csv").write_text("name,stage,status\nwater,dmol3_sp,ok\n", encoding="utf-8")
            output = run_dir / "summary.json"
            self.run_python(ROOT / "skills" / "materials-studio-runner" / "scripts" / "parse_ms_results.py",
                            "--run-dir", run_dir, "--output", output)
            summary = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "completed")
            self.assertEqual(Path(summary["execution_run_dir"]), run_dir)

    @unittest.skipUnless(importlib.util.find_spec("pyscf"), "PySCF is tested in Linux CI")
    def test_pyscf_water_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            example = ROOT / "examples" / "pyscf-water-frontier"
            manifest = json.loads((example / "manifest.json").read_text(encoding="utf-8"))
            manifest["xyz"] = str(example / "water.xyz")
            manifest["method"] = {"basis": "sto-3g", "grid_level": 1}
            manifest["cube"] = {"properties": ["density", "mep", "homo", "lumo"], "resolution_bohr": 0.7, "margin_bohr": 2.0}
            manifest_path = temp / "manifest.json"; manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.run_python(ROOT / "skills" / "pyscf-runner" / "scripts" / "run_pyscf_job.py",
                            "--manifest", manifest_path, "--run-dir", temp)
            summary = json.loads((temp / "pyscf_summary.json").read_text(encoding="utf-8"))
            self.assertTrue(summary["normal_termination"]); self.assertTrue(summary["scf_converged"])
            for filename in ("density.cube", "mep.cube", "homo.cube", "lumo.cube"):
                self.assertGreater((temp / filename).stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()

"""Fixture, validation, and command-line checks for the scenario runner."""

import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/evaluation"))

from run_allocation_scenarios import as_markdown, evaluate_scenarios


class AllocationScenarioTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(
            (ROOT / "configs/optimization/allocation-scenarios.json").read_text(encoding="utf-8"))

    def test_fixture_totals_and_feasibility(self):
        expected = {
            "scarce_budget": (90, 60, 0),
            "surplus_budget": (50, 50, 50),
            "zero_demand": (0, 0, 10),
            "zero_budget": (0, 30, 0),
            "closed_location": (20, 30, 20),
        }
        report = evaluate_scenarios(self.document)
        self.assertTrue(report["all_feasible"])
        self.assertEqual({row["id"] for row in report["results"]}, set(expected))
        for row in report["results"]:
            for key, value in zip(("total_served", "total_unmet", "unused_budget"), expected[row["id"]]):
                self.assertAlmostEqual(row[key], value)
            self.assertAlmostEqual(row["total_demand"], row["total_served"] + row["total_unmet"])
            self.assertLessEqual(row["max_constraint_violation"], report["feasibility_tolerance"])

    def test_repeated_runs_and_input_preservation(self):
        original = copy.deepcopy(self.document)
        self.assertEqual(evaluate_scenarios(self.document), evaluate_scenarios(self.document))
        self.assertEqual(self.document, original)

    def test_invalid_documents(self):
        cases = [None, {}, {"schema_version": True}, {"schema_version": 2},
                 {"schema_version": 1, "scenarios": []},
                 {"schema_version": 1, "scenarios": [None]}]
        duplicate = copy.deepcopy(self.document)
        duplicate["scenarios"].append(copy.deepcopy(duplicate["scenarios"][0]))
        cases.append(duplicate)
        for document in cases:
            with self.subTest(document=document), self.assertRaises(ValueError):
                evaluate_scenarios(document)

    def test_invalid_scenario_inputs(self):
        for key, value in [("id", "bad|id"), ("budget", -1), ("budget", math.inf),
                           ("budget", True), ("demand", [math.nan]),
                           ("demand", ["10"]), ("demand", []), ("capacity", None)]:
            document = copy.deepcopy(self.document)
            document["scenarios"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                evaluate_scenarios(document)

    def test_cli_from_another_directory(self):
        script = ROOT / "scripts/evaluation/run_allocation_scenarios.py"
        expected = evaluate_scenarios(self.document)
        with tempfile.TemporaryDirectory() as directory:
            for output_format in ("json", "markdown"):
                result = subprocess.run([sys.executable, str(script), "--format", output_format],
                                        cwd=directory, capture_output=True, text=True, check=True)
                if output_format == "json":
                    self.assertEqual(json.loads(result.stdout), expected)
                else:
                    self.assertEqual(result.stdout.strip(), as_markdown(expected))


if __name__ == "__main__":
    unittest.main()

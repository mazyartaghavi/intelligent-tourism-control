import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tourism_control.control.experiment import compare, validate_control


def load(name):
    return json.loads((ROOT / "configs" / name).read_text(encoding="utf-8"))


class DailyComparisonTests(unittest.TestCase):
    def test_partition_overlap_is_rejected(self):
        control = load("control/stage-e.json")
        control["test_scenario_seeds"] = control["training_scenario_seeds"][:2]
        with self.assertRaisesRegex(ValueError, "disjoint"):
            validate_control(control, [])

    def test_end_to_end_and_fair_scoring(self):
        control = load("control/stage-e.json")
        for key in ("training_scenario_seeds", "validation_scenario_seeds", "test_scenario_seeds", "learning_seeds"):
            control[key] = control[key][:2]
        control["passes"] = 1
        forecast = {**load("forecasting/stage-a.json"), "test_days": 7}
        allocation = load("optimization/forecast-allocation.json")
        report, timings = compare(forecast, allocation, control)
        self.assertEqual(len(report["trajectories"]), 16)
        self.assertEqual(len(timings), 18)
        for learned in report["learning"]:
            self.assertEqual(learned["transitions"], 14)
        for record in report["trajectories"]:
            self.assertTrue(record["feasible"])
            self.assertGreaterEqual(record["oracle_gap"], -1e-7)
            self.assertAlmostEqual(record["cumulative_reward"], -record["objective"])

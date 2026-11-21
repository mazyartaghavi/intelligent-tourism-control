from datetime import date
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tourism_control.forecasting.baselines import DemandHistory, Method, forecast
from tourism_control.optimization.forecast_allocation import (
    AllocationSettings, benchmark, demand_matrix, oracle_reference, score_path,
)


def config(name):
    return json.loads((ROOT / "configs" / name).read_text(encoding="utf-8"))


class ForecastAllocationTests(unittest.TestCase):
    def test_forecast_alignment_uses_keys_and_rejects_incomplete_batches(self):
        history = DemandHistory("sample", ("a", "b"), date(2026, 1, 1), ((4, 2),))
        points = forecast(history, 2, Method.PERSISTENCE)
        self.assertEqual(demand_matrix(reversed(points), history, 2, Method.PERSISTENCE), [[4, 2], [4, 2]])
        for invalid in (points[:-1], points + points[:1]):
            with self.assertRaises(ValueError):
                demand_matrix(invalid, history, 2, Method.PERSISTENCE)
        with self.assertRaises(ValueError):
            demand_matrix(points, history, 2, Method.SEASONAL_MEAN)

    def test_realized_score_and_oracle_objective_use_same_costs(self):
        settings = AllocationSettings.from_document(config("optimization/forecast-allocation.json"), 3)
        realized, ceiling = [[1, 0, 0], [4, 0, 0]], [[10, 10, 10]] * 2
        planned = settings.problem([[4, 0, 0]] * 2, ceiling, [0, 0, 0])
        score = score_path(planned, [[4, 0, 0]] * 2, realized)
        oracle, _ = oracle_reference(settings, realized, ceiling)
        self.assertTrue(score["feasible"])
        self.assertEqual(score["served"], 5)
        self.assertEqual(score["unused_service"], 3)
        self.assertAlmostEqual(score["objective"], 7.8)
        self.assertAlmostEqual(oracle["objective"], 5.4)
        with self.assertRaises(ValueError):
            AllocationSettings.from_document({**config("optimization/forecast-allocation.json"),
                                              "adjustment_cost": [1, 1, 1]}, 3)

    def test_two_scenario_integration(self):
        forecast_config = {**config("forecasting/stage-a.json"), "seeds": [4270, 4271], "test_days": 7}
        report, timings = benchmark(forecast_config, config("optimization/forecast-allocation.json"))
        self.assertEqual(len(report["trajectories"]), 10)
        self.assertEqual(len(timings), 10)
        for row in report["trajectories"]:
            self.assertTrue(row["feasible"])
            self.assertAlmostEqual(row["served"] + row["unmet"],  sum(
                next(r for r in report["trajectories"]
                     if r["scenario_id"] == row["scenario_id"] and r["policy"] == "oracle_full_test")[k]
                for k in ("served", "unmet")))
            self.assertGreaterEqual(row["oracle_gap"], -1e-7)

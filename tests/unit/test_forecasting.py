import json
import math
from datetime import date, timedelta
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tourism_control.forecasting.baselines import DemandHistory, ForecastPoint, Method, PredictionInterval, forecast
from tourism_control.forecasting.experiment import ExperimentConfig, evaluate, synthetic_panel


def fixture():
    return json.loads((ROOT / "configs/forecasting/stage-a.json").read_text(encoding="utf-8"))


class ForecastingTests(unittest.TestCase):
    def test_baseline_values_and_week_wrap(self):
        start = date(2026, 1, 5)
        history = DemandHistory("example", ("a", "b"), start,
                                tuple((day, day * 2) for day in range(21)))
        for method, first_value in (
            (Method.PERSISTENCE, 20),
            (Method.SEASONAL_NAIVE, 14),
            (Method.SEASONAL_MEAN, 7),
        ):
            with self.subTest(method=method):
                rows = forecast(history, 8, method)
                self.assertEqual(len(rows), 16)
                self.assertAlmostEqual(rows[0].predicted_demand, first_value)
                self.assertAlmostEqual(rows[1].predicted_demand, 2 * first_value)
                self.assertAlmostEqual(rows[-2].predicted_demand, first_value)
                self.assertEqual(rows[0].target, history.end)
                self.assertEqual(rows[-1].target, history.end + timedelta(days=7))
                self.assertEqual(rows[-1].horizon_days, 8)
                self.assertIsNone(rows[0].interval)

    def test_invalid_history_and_output(self):
        start = date(2026, 1, 5)
        for locations, values in (
            (("a", "a"), ((1, 2),)),
            (("a",), ((float("nan"),),)),
            (("a",), ((-1,),)),
            (("a",), ((True,),)),
            (("a",), ((1, 2),)),
        ):
            with self.subTest(locations=locations, values=values), self.assertRaises(ValueError):
                DemandHistory("example", locations, start, values)
        history = DemandHistory("example", ("a",), start, ((1,),))
        with self.assertRaises(ValueError):
            forecast(history, 1, Method.SEASONAL_NAIVE)
        with self.assertRaises(ValueError):
            forecast(history, True, Method.PERSISTENCE)
        with self.assertRaises(ValueError):
            ForecastPoint("example", "a", start, start, 2, Method.PERSISTENCE, 0)
        with self.assertRaises(ValueError):
            PredictionInterval(2, 1, 0.9)
        with self.assertRaises(ValueError):
            PredictionInterval(0, 1, 1)

    def test_seed_repeatability_and_partition_boundaries(self):
        config = ExperimentConfig.from_document(fixture())
        validation_days = [index + step for index in config.windows("validation")
                           for step in range(config.horizon_days)]
        test_days = [index + step for index in config.windows("test")
                     for step in range(config.horizon_days)]
        self.assertEqual(validation_days, list(range(70, 98)))
        self.assertEqual(test_days, list(range(98, 140)))
        first, second = config.seeds[:2]
        self.assertEqual(synthetic_panel(config, first), synthetic_panel(config, first))
        self.assertNotEqual(synthetic_panel(config, first)[0].demand,
                            synthetic_panel(config, second)[0].demand)
        for changes in ({"test_days": 43}, {"seeds": [1, 1]}, {"training_days": 20},
                        {"horizon_days": False}, {"locations": ["site-a", "site-a"]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                ExperimentConfig.from_document({**fixture(), **changes})

    def test_contemporaneous_and_future_targets_are_hidden_at_origin(self):
        document = {**fixture(), "seeds": [4270]}
        config = ExperimentConfig.from_document(document)
        panel, ceilings = synthetic_panel(config, 4270)
        cutoff = config.windows("test").start
        changed = DemandHistory(panel.scenario_id, panel.locations, panel.start,
                                panel.demand[:cutoff] + ((999, 999, 999),) * config.test_days)

        def first_predictions(series):
            with patch("tourism_control.forecasting.experiment.synthetic_panel", return_value=(series, ceilings)), \
                 patch("tourism_control.forecasting.experiment.forecast", wraps=forecast) as recorded:
                summary, _, _ = evaluate(document)
            origin = config.start + timedelta(days=cutoff)
            calls = [call.args for call in recorded.call_args_list if call.args[0].end == origin]
            self.assertEqual(len(calls), len(Method))
            self.assertTrue(all(history.demand == panel.demand[:cutoff] for history, _, _ in calls))
            return summary["selected_by_validation_mae"], [forecast(*args) for args in calls]

        self.assertEqual(first_predictions(panel), first_predictions(changed))

    def test_metrics_on_known_errors_and_horizon_counts(self):
        document = {**fixture(), "seeds": [0], "locations": ["a"], "validation_days": 7, "test_days": 7}
        config = ExperimentConfig.from_document(document)
        values = ((2,),) * 77 + tuple((value,) for value in (1, 3, 2, 0, 4, 2, 2))
        panel = DemandHistory("seed-0", config.locations, config.start, values)
        with patch("tourism_control.forecasting.experiment.synthetic_panel",
                   return_value=(panel, ((3,),) * len(values))):
            _, metrics, scenarios = evaluate(document)
        test_persistence = {row["stratum"]: row for row in metrics
                            if row["split"] == "test" and row["method"] == "persistence"}
        self.assertEqual(test_persistence["all"]["n"], 7)
        self.assertAlmostEqual(test_persistence["all"]["mae"], 6 / 7)
        self.assertAlmostEqual(test_persistence["all"]["rmse"], math.sqrt(10 / 7))
        self.assertEqual(test_persistence["above_capacity"]["n"], 1)
        self.assertEqual(test_persistence["horizon_5"]["mae"], 2)
        self.assertEqual(len(scenarios), 2 * len(Method))


if __name__ == "__main__":
    unittest.main()

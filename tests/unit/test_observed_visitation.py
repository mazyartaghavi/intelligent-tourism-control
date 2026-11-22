from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/evaluation"))

from run_observed_visitation import DATA, benchmark, load_panel, predict
from run_forecast_allocation import ALLOCATION_CONFIG, read_json
from tourism_control.optimization.forecast_allocation import AllocationSettings


class ObservedVisitationTests(unittest.TestCase):
    def test_reporting_lag_and_seasonal_alignment(self):
        origin = 48
        history = [[t, t + 1, t + 2] for t in range(origin - 1)]
        self.assertEqual(predict(history, origin, "persistence"), [[46, 47, 48]] * 3)
        self.assertEqual(predict(history, origin, "seasonal_naive"), history[36:39])
        self.assertEqual(predict(history, origin, "seasonal_mean"),
                         [[24, 25, 26], [25, 26, 27], [26, 27, 28]])
        with self.assertRaisesRegex(ValueError, "two months"):
            predict(history + [[999] * 3], origin, "persistence")

    def test_complete_panel_and_realized_accounting(self):
        panel = load_panel(DATA)
        self.assertEqual(len(panel), 192)
        settings = AllocationSettings.from_document(read_json(ALLOCATION_CONFIG), 3)
        _, metrics, annual = benchmark(panel, settings)
        self.assertEqual(len(annual), 16)
        for row in annual:
            self.assertTrue(row["feasible"])
            start = (row["year"] - 2010) * 12
            self.assertAlmostEqual(row["served"] + row["unmet"],
                                   sum(sum(month) for month in panel[start:start + 12]), places=5)
        self.assertTrue(all(row["n"] == 144 for row in metrics
                            if row["split"] == "test" and row["park"] == "all"))

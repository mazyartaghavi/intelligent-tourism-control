"""Decision-evaluation contracts and independent single-period optimality checks."""

import copy
import json
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/evaluation"))
from run_milestone import run, stress_scenario, tables
from tourism_control.optimization.linear import solve_allocation


class MilestoneTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "configs/optimization/milestone-benchmark.json").read_text(encoding="utf-8"))

    def test_fifty_independent_greedy_oracles(self):
        rng = random.Random(91)
        for _ in range(50):
            demand = [rng.uniform(0, 30) for _ in range(4)]
            capacity = [rng.uniform(0, 30) for _ in range(4)]
            weights = [rng.uniform(0, 8) for _ in range(4)]
            costs = [rng.uniform(0, 4) for _ in range(4)]
            budget = rng.uniform(0, 80)
            remaining = budget
            reference = sum(w * d for w, d in zip(weights, demand))
            # Independent fractional-knapsack oracle: unit resource coefficients,
            # no temporal coupling, positive net benefit only.
            for i in sorted(range(4), key=lambda i: weights[i] - costs[i], reverse=True):
                amount = min(demand[i], capacity[i], remaining) if weights[i] > costs[i] else 0
                reference -= amount * (weights[i] - costs[i])
                remaining -= amount
            p = {"demand": [demand], "capacity": [capacity], "budget": [budget],
                 "unmet_penalty": [weights], "operating_cost": [costs],
                 "adjustment_cost": [0] * 4, "initial_allocation": [0] * 4}
            self.assertAlmostEqual(solve_allocation(p)["metrics"]["objective"], reference, places=7)

    def test_stress_draws_are_paired_without_changing_actual_demand(self):
        settings = self.config["stress"]
        p0, actual0, error0 = stress_scenario(settings, 1000, 0)
        p1, actual1, error1 = stress_scenario(settings, 1000, .7)
        self.assertEqual(actual0, actual1)
        self.assertEqual(p0["demand"], actual0)
        self.assertEqual(error0, 0)
        self.assertGreater(error1, 0)
        for key in p0.keys() - {"demand"}:
            self.assertEqual(p0[key], p1[key])
        self.assertEqual((p1, actual1, error1), stress_scenario(settings, 1000, .7))

    def test_small_end_to_end_run_and_incomparable_case(self):
        config = copy.deepcopy(self.config)
        config["stress"]["replications"] = 2
        config["stress"]["bootstrap_resamples"] = 100
        before = copy.deepcopy(config)
        report = run(config)
        self.assertEqual(config, before)
        self.assertEqual(report["summary"]["lp_solves"], 26)
        self.assertEqual(report["summary"]["lp_feasible"], 26)
        self.assertEqual(report["summary"]["stress_pairs"], 8)
        ramp = next(r for r in report["fixed"] if r["id"] == "ramp_transition")
        self.assertFalse(ramp["comparable"])
        self.assertEqual(ramp["proportional"]["metrics"]["constraint_violations"]["change_limit"], 10)
        self.assertIn("no: heuristic violates ramp limit", tables(report))
        json.dumps(report, allow_nan=False)
        repeat = run(config)
        self.assertEqual(report["summary"]["stress"], repeat["summary"]["stress"])


if __name__ == "__main__":
    unittest.main()

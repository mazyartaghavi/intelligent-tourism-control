"""Run with: python -m unittest discover -s tests/unit -v"""

import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from tourism_control.optimization.proportional import allocate_capacity


class ProportionalAllocationTests(unittest.TestCase):
    def test_scarce_budget_and_local_limit(self):
        self.assertEqual(allocate_capacity([80, 40, 30], [60, 50, 30], 90),
                         [540 / 13, 360 / 13, 270 / 13])

    def test_surplus_budget_is_not_forced_into_locations(self):
        self.assertEqual(allocate_capacity([20, 80], [50, 30], 100), [20, 30])

    def test_zero_cases(self):
        for demand, capacity, budget in [([10, 20], [20, 20], 0),
                                         ([0, 0], [20, 20], 10),
                                         ([10, 20], [0, 0], 10)]:
            with self.subTest(demand=demand, capacity=capacity, budget=budget):
                self.assertEqual(allocate_capacity(demand, capacity, budget), [0, 0])

    def test_invalid_shapes(self):
        for demand, capacity in [([], []), ([10], [10, 20])]:
            with self.subTest(demand=demand, capacity=capacity):
                with self.assertRaises(ValueError):
                    allocate_capacity(demand, capacity, 10)

    def test_invalid_values_in_each_input(self):
        for value in [-1, math.nan, math.inf, -math.inf]:
            for args in [([value], [10], 10), ([10], [value], 10),
                         ([10], [10], value)]:
                with self.subTest(args=args):
                    with self.assertRaises(ValueError):
                        allocate_capacity(*args)

    def test_feasibility_across_synthetic_cases(self):
        rng = random.Random(42)
        for _ in range(100):
            demand = [rng.uniform(0, 100) for _ in range(5)]
            capacity = [rng.uniform(0, 100) for _ in range(5)]
            budget = rng.uniform(0, 500)
            allocation = allocate_capacity(demand, capacity, budget)
            self.assertEqual(allocation, allocate_capacity(demand, capacity, budget))
            for assigned, requested, limit in zip(allocation, demand, capacity):
                self.assertGreaterEqual(assigned, 0)
                self.assertLessEqual(assigned, min(requested, limit) + 1e-10)
            self.assertAlmostEqual(math.fsum(allocation),
                                   min(budget, math.fsum(map(min, demand, capacity))))


if __name__ == "__main__":
    unittest.main()

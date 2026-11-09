"""Analytical solutions, independent enumeration, numerical checks, and failure cases."""

import copy
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from tourism_control.optimization.linear import (AllocationSolveError, evaluate_allocation,
                                                  solve_allocation, validate_problem)


def problem(demand, budget, penalty=None, cost=None, adjustment=None, initial=None, capacity=None):
    t, n = np.asarray(demand).shape
    return {"demand": demand, "capacity": capacity or [[100] * n for _ in range(t)],
            "budget": budget, "unmet_penalty": penalty or [[1] * n for _ in range(t)],
            "operating_cost": cost or [[0] * n for _ in range(t)],
            "adjustment_cost": adjustment or [0] * n,
            "initial_allocation": initial or [0] * n}


class LinearAllocationTests(unittest.TestCase):
    def test_analytical_priority_solution_and_dual(self):
        p = problem([[10, 10]], [10], [[4, 1]], [[0.5, 0.5]])
        r = solve_allocation(p)
        np.testing.assert_allclose(r["allocation"], [[10, 0]])
        self.assertAlmostEqual(r["metrics"]["objective"], 15)
        self.assertLess(r["diagnostics"]["primal_dual_gap"], 1e-8)

    def test_temporal_coupling_has_known_solution(self):
        p = problem([[10], [2], [10]], [10, 10, 10], adjustment=[0.75])
        r = solve_allocation(p)
        np.testing.assert_allclose(r["allocation"], [[2], [2], [10]])
        self.assertAlmostEqual(r["metrics"]["objective"], 15.5)
        self.assertAlmostEqual(evaluate_allocation(p, [[10], [2], [10]])["objective"], 19.5)

    def test_expensive_service_can_remain_unused(self):
        p = problem([[10]], [10], cost=[[2]])
        r = solve_allocation(p)
        self.assertEqual(r["allocation"], [[0]])
        self.assertAlmostEqual(r["metrics"]["objective"], 10)

    def test_zero_cases_and_closed_location(self):
        for p in [problem([[0, 0]], [20]), problem([[10, 20]], [0]),
                  problem([[10, 20]], [30], capacity=[[0, 0]])]:
            with self.subTest(p=p):
                r = solve_allocation(p)
                np.testing.assert_allclose(r["allocation"], [[0, 0]])
                self.assertTrue(r["metrics"]["feasible"])

    def test_change_limit_and_infeasibility(self):
        p = problem([[30], [30]], [30, 30], initial=[10])
        p["max_change"] = [3]
        np.testing.assert_allclose(solve_allocation(p)["allocation"], [[13], [16]])
        p["capacity"] = [[0], [0]]
        with self.assertRaises(AllocationSolveError) as caught:
            solve_allocation(p)
        self.assertEqual(caught.exception.status, 2)

    def test_independent_integer_grid_reference(self):
        p = problem([[2, 3], [3, 2]], [3, 3], [[3, 1], [1, 3]],
                    [[0.25, 0.5], [0.25, 0.5]], [0.5, 0.75], [1, 1])
        candidates = []
        # Calculate the objective directly, without using model construction or its scorer.
        for values in itertools.product(range(4), repeat=4):
            a, b, c, d = values
            if a <= 2 and d <= 2 and a + b <= 3 and c + d <= 3:
                objective = (3*(2-a) + (3-b) + (3-c) + 3*(2-d)
                             + 0.25*(a+c) + 0.5*(b+d)
                             + 0.5*(abs(a-1)+abs(c-a)) + 0.75*(abs(b-1)+abs(d-b)))
                candidates.append(objective)
        self.assertAlmostEqual(solve_allocation(p)["metrics"]["objective"], min(candidates))

    def test_realized_scoring_charges_unused_planned_capacity(self):
        p = problem([[10]], [10], cost=[[0.5]])
        m = evaluate_allocation(p, [[8]], realized_demand=[[3]])
        self.assertEqual((m["served"], m["unmet"], m["unused_service"]), (3, 0, 5))
        self.assertEqual(m["operating_cost"], 4)
        self.assertTrue(m["feasible"])

    def test_violation_reporting_does_not_repair(self):
        p = problem([[10]], [5], capacity=[[8]])
        m = evaluate_allocation(p, [[11]])
        self.assertFalse(m["feasible"])
        self.assertEqual(m["constraint_violations"]["shared_budget"], 6)
        self.assertEqual(m["constraint_violations"]["planning_demand"], 1)

    def test_invalid_shapes_values_and_fields(self):
        original = problem([[10, 20]], [10])
        for key, value in [("demand", []), ("demand", [10, 20]), ("capacity", [[10]]),
                           ("budget", [True]), ("budget", ["10"]), ("budget", [-1]),
                           ("budget", [float("nan")]), ("operating_cost", [[0, float("inf")]]),
                           ("max_change", [2]), ("demand", [[2], [3, 4]])]:
            p = copy.deepcopy(original)
            p[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_problem(p)
        p = {**original, "unknown": 1}
        with self.assertRaises(ValueError):
            solve_allocation(p)
        for limit in [0, -1, True, float("nan")]:
            with self.assertRaises(ValueError):
                solve_allocation(original, limit)

    def test_zero_cost_auxiliaries_and_input_preservation(self):
        p = problem([[10], [10]], [10, 10], initial=[3])
        before = copy.deepcopy(p)
        first, second = solve_allocation(p), solve_allocation(p)
        self.assertEqual(first["allocation"], second["allocation"])
        self.assertEqual(p, before)
        self.assertEqual(first["metrics"]["total_change"], 7)
        self.assertEqual(first["metrics"]["adjustment_cost"], 0)

    def test_cli_success_and_explicit_failure(self):
        script = ROOT / "src/tourism_control/optimization/linear.py"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            p = problem([[5]], [5])
            path.write_text(json.dumps(p), encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), str(path)],
                                    cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "optimal")
            p.update(initial_allocation=[10], max_change=[1])
            path.write_text(json.dumps(p), encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), str(path)],
                                    cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["solver_status"], 2)


if __name__ == "__main__":
    unittest.main()

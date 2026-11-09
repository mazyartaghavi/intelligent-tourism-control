"""Continuous multi-period allocation with explicit capacity and change limits.

Arrays use [period][location] order. See docs/methodology/allocation-algorithm.md.
SciPy/HiGHS supplies the solver; this module supplies the model and diagnostics.
"""

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

TOLERANCE = 1e-7
SOLVER_TOLERANCE = 1e-9


class AllocationSolveError(RuntimeError):
    """A solver failure is explicit and never treated as an allocation."""

    def __init__(self, status, message):
        self.status = int(status)
        super().__init__(message)


def _array(value, name, shape=None):
    # Reject bools and numeric strings before NumPy can coerce mixed inputs.
    def numeric(item):
        if isinstance(item, list):
            return bool(item) and all(numeric(child) for child in item)
        return type(item) in (int, float)

    if not isinstance(value, list) or not numeric(value):
        raise ValueError(f"{name} must be a nonempty numeric array")
    try:
        array = np.asarray(value, dtype=float)
    except (ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a rectangular finite array") from error
    if not np.isfinite(array).all() or (array < 0).any():
        raise ValueError(f"{name} must be finite and non-negative")
    if shape is not None and array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    return array


def validate_problem(problem):
    """Validate a JSON-compatible problem without modifying caller data."""
    if not isinstance(problem, dict):
        raise ValueError("problem must be an object")
    required = {"demand", "capacity", "budget", "unmet_penalty", "operating_cost",
                "adjustment_cost", "initial_allocation"}
    if not required <= problem.keys() or problem.keys() - required - {"max_change"}:
        raise ValueError("problem has missing or unknown fields")
    demand = _array(problem["demand"], "demand")
    if demand.ndim != 2:
        raise ValueError("demand must have [period][location] shape")
    periods, locations = demand.shape
    p = {"demand": demand}
    for name in ("capacity", "unmet_penalty", "operating_cost"):
        p[name] = _array(problem[name], name, demand.shape)
    p["budget"] = _array(problem["budget"], "budget", (periods,))
    for name in ("adjustment_cost", "initial_allocation"):
        p[name] = _array(problem[name], name, (locations,))
    p["max_change"] = (None if problem.get("max_change") is None else
                       _array(problem["max_change"], "max_change", (locations,)))
    return p


def _build_model(p):
    periods, locations = p["demand"].shape
    cells = periods * locations
    objective = np.concatenate((p["operating_cost"].ravel(),
                                p["unmet_penalty"].ravel(),
                                np.tile(p["adjustment_cost"], periods)))
    upper = np.full(3 * cells, np.inf)
    upper[:cells] = p["capacity"].ravel()
    if p["max_change"] is not None:
        upper[2 * cells:] = np.tile(p["max_change"], periods)
    bounds = list(zip(np.zeros(3 * cells), upper))
    indices = np.arange(cells)
    equality = coo_matrix((np.ones(2 * cells),
                          (np.tile(indices, 2), np.concatenate((indices, indices + cells)))),
                         shape=(cells, 3 * cells)).tocsr()
    rows, columns, values, rhs = [], [], [], []

    def constraint(entries, limit):
        row = len(rhs)
        for column, value in entries:
            rows.append(row)
            columns.append(column)
            values.append(value)
        rhs.append(limit)

    for t in range(periods):
        constraint([(t * locations + i, 1) for i in range(locations)], p["budget"][t])
    for t in range(periods):
        for i in range(locations):
            cell = t * locations + i
            positive = [(cell, 1), (2 * cells + cell, -1)]
            negative = [(cell, -1), (2 * cells + cell, -1)]
            if t:
                positive.append((cell - locations, -1))
                negative.append((cell - locations, 1))
            constraint(positive, p["initial_allocation"][i] if not t else 0)
            constraint(negative, -p["initial_allocation"][i] if not t else 0)
    inequality = coo_matrix((values, (rows, columns)),
                           shape=(len(rhs), 3 * cells)).tocsr()
    return objective, inequality, np.asarray(rhs), equality, p["demand"].ravel(), bounds, upper


def evaluate_allocation(problem, allocation, realized_demand=None):
    """Recompute constraints and physical objective components from allocations.

    If realized_demand is provided, unused planned service still incurs operating
    cost. Feasibility continues to refer to the planning contract, not to a queue
    or an occupancy model. No quantities are repaired or clipped for validation.
    """
    p = validate_problem(problem)
    x = np.asarray(allocation, dtype=float)
    if x.shape != p["demand"].shape or not np.isfinite(x).all():
        raise ValueError("allocation must have the demand shape and finite values")
    change = np.abs(np.diff(np.vstack((p["initial_allocation"], x)), axis=0))
    residuals = {
        "nonnegative": float(max(0, -x.min())),
        "local_capacity": float(max(0, (x - p["capacity"]).max())),
        "planning_demand": float(max(0, (x - p["demand"]).max())),
        "shared_budget": float(max(0, (x.sum(axis=1) - p["budget"]).max())),
        "change_limit": (0.0 if p["max_change"] is None else
                         float(max(0, (change - p["max_change"]).max()))),
    }
    demand = p["demand"] if realized_demand is None else _array(
        realized_demand, "realized_demand", p["demand"].shape)
    unmet = np.maximum(demand - x, 0)
    components = {
        "weighted_unmet": float(np.sum(p["unmet_penalty"] * unmet)),
        "operating_cost": float(np.sum(p["operating_cost"] * x)),
        "adjustment_cost": float(np.sum(p["adjustment_cost"] * change)),
    }
    metrics = {
        **components,
        "objective": sum(components.values()),
        "total_demand": float(demand.sum()),
        "served": float(np.minimum(demand, x).sum()),
        "unmet": float(unmet.sum()),
        "unused_service": float(np.maximum(x - demand, 0).sum()),
        "total_change": float(change.sum()),
        "unused_budget": (p["budget"] - x.sum(axis=1)).tolist(),
        "constraint_violations": residuals,
        "max_constraint_violation": max(residuals.values()),
        "feasible": max(residuals.values()) <= TOLERANCE,
    }
    if not all(np.isfinite(value) for value in components.values()):
        raise ValueError("objective components exceed numeric range")
    return metrics


def solve_allocation(problem, time_limit=30.0):
    """Solve the continuous LP and check primal feasibility and dual diagnostics."""
    if type(time_limit) not in (int, float) or not np.isfinite(time_limit) or time_limit <= 0:
        raise ValueError("time_limit must be finite and positive")
    start = perf_counter()
    p = validate_problem(problem)
    c, aub, bub, aeq, beq, bounds, upper = _build_model(p)
    result = linprog(c, A_ub=aub, b_ub=bub, A_eq=aeq, b_eq=beq,
                     bounds=bounds, method="highs-ds", options={
                         "time_limit": float(time_limit),
                         "primal_feasibility_tolerance": SOLVER_TOLERANCE,
                         "dual_feasibility_tolerance": SOLVER_TOLERANCE,
                         "presolve": True,
                     })
    elapsed = perf_counter() - start
    if not result.success:
        raise AllocationSolveError(result.status, result.message)
    cells = p["demand"].size
    allocation = result.x[:cells].reshape(p["demand"].shape)
    metrics = evaluate_allocation(problem, allocation)
    finite = np.isfinite(upper)
    dual_objective = float(bub @ result.ineqlin.marginals + beq @ result.eqlin.marginals
                           + upper[finite] @ result.upper.marginals[finite])
    stationarity = c - aub.T @ result.ineqlin.marginals - aeq.T @ result.eqlin.marginals
    stationarity -= result.lower.marginals + result.upper.marginals
    diagnostics = {
        "bound_violation": float(max(0, -result.x.min(),
                                     (result.x[finite] - upper[finite]).max())),
        "equality_residual": float(np.max(np.abs(aeq @ result.x - beq))),
        "inequality_violation": float(max(0, np.max(aub @ result.x - bub))),
        "stationarity_residual": float(np.max(np.abs(stationarity))),
        "dual_sign_violation": float(max(0, result.ineqlin.marginals.max(),
                                         -result.lower.marginals.min(),
                                         result.upper.marginals.max())),
        "primal_dual_gap": abs(float(result.fun) - dual_objective),
        "objective_reconstruction_error": abs(float(result.fun) - metrics["objective"]),
    }
    gap_tolerance = TOLERANCE * (1 + abs(float(result.fun)))
    checks = metrics["feasible"] and all(
        value <= (gap_tolerance if key in {"primal_dual_gap", "objective_reconstruction_error"}
                  else TOLERANCE) for key, value in diagnostics.items())
    if not checks or not all(np.isfinite(value) for value in diagnostics.values()):
        raise AllocationSolveError(4, "Independent numerical validation failed")
    return {
        "status": "optimal", "solver": "scipy-highs-ds", "solver_status": int(result.status),
        "solver_message": result.message, "iterations": int(result.nit),
        "elapsed_seconds": elapsed, "allocation": allocation.tolist(),
        "unmet_demand": (p["demand"] - allocation).tolist(),
        "metrics": metrics, "diagnostics": diagnostics,
        "budget_marginals": result.ineqlin.marginals[:len(p["budget"])].tolist(),
        "feasibility_tolerance": TOLERANCE, "solver_tolerance": SOLVER_TOLERANCE,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("--time-limit", type=float, default=30.0)
    args = parser.parse_args()
    try:
        report = solve_allocation(json.loads(args.problem.read_text(encoding="utf-8")), args.time_limit)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    except AllocationSolveError as error:
        print(json.dumps({"status": "failed", "solver_status": error.status, "message": str(error)}))
        return 1
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

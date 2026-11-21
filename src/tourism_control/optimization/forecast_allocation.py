"""Align dated forecasts with service limits and compare realized allocations."""

from dataclasses import dataclass
from datetime import timedelta
from math import fsum, sqrt
from random import Random
from statistics import mean, stdev
from time import perf_counter

from tourism_control.forecasting.baselines import DemandHistory, ForecastPoint, Method, forecast
from tourism_control.forecasting.experiment import ExperimentConfig, synthetic_panel
from .linear import TOLERANCE, evaluate_allocation, solve_allocation, validate_problem
from .proportional import allocate_capacity

METRICS = ("objective", "weighted_unmet", "served", "unmet", "unused_service",
           "operating_cost", "adjustment_cost", "total_change")


@dataclass(frozen=True)
class AllocationSettings:
    budget_fraction: float
    unmet_penalty: tuple
    operating_cost: tuple
    adjustment_cost: tuple

    @classmethod
    def from_document(cls, document, locations):
        if not isinstance(document, dict) or set(document) != {
            "schema_version", "budget_fraction", "unmet_penalty", "operating_cost", "adjustment_cost"
        }:
            raise ValueError("allocation configuration fields must match schema version 1")
        if type(document["schema_version"]) is not int or document["schema_version"] != 1:
            raise ValueError("allocation schema_version must be 1")
        fraction = document["budget_fraction"]
        if type(fraction) not in (float, int) or not 0 < fraction <= 1:
            raise ValueError("budget_fraction must be in (0, 1]")
        vectors = [document[key] for key in ("unmet_penalty", "operating_cost", "adjustment_cost")]
        if any(not isinstance(vector, list) or len(vector) != locations for vector in vectors):
            raise ValueError("cost vectors must match the forecast location count")
        settings = cls(fraction, *(tuple(vector) for vector in vectors))
        validate_problem(settings.problem([[0] * locations], [[0] * locations], [0] * locations))
        # Makes excess allocation in the perfect-information policy removable
        # without increasing objective, even after accounting for both transitions.
        if any(cost <= 2 * adjustment for cost, adjustment in
               zip(settings.operating_cost, settings.adjustment_cost)):
            raise ValueError("oracle comparison requires operating cost > twice adjustment cost")
        return settings

    def problem(self, demand, ceilings, previous):
        return {
            "demand": [list(row) for row in demand],
            "capacity": [list(row) for row in ceilings],
            "budget": [self.budget_fraction * sum(row) for row in ceilings],
            "unmet_penalty": [list(self.unmet_penalty) for _ in demand],
            "operating_cost": [list(self.operating_cost) for _ in demand],
            "adjustment_cost": list(self.adjustment_cost),
            "initial_allocation": list(previous),
        }


def demand_matrix(points, history: DemandHistory, horizon, method):
    """Align one complete forecast by its explicit date, origin and site labels."""
    columns = history.locations
    origin = history.end
    indexed = {}
    for point in points:
        if (not isinstance(point, ForecastPoint) or point.scenario_id != history.scenario_id
                or point.origin != origin or not 1 <= point.horizon_days <= horizon
                or point.location_id not in columns or point.method is not method):
            raise ValueError("forecast point does not match the requested scenario, origin, site or method")
        key = point.horizon_days, point.location_id
        if key in indexed:
            raise ValueError("duplicate forecast coordinate")
        indexed[key] = point.predicted_demand
    if len(indexed) != horizon * len(columns):
        raise ValueError("incomplete forecast batch")
    return [[indexed[lead, location] for location in columns] for lead in range(1, horizon + 1)]


def forecast_matrix(panel, index, horizon, method):
    history = panel.before(panel.start + timedelta(days=index))
    return demand_matrix(forecast(history, horizon, method), history, horizon, method)


def proportional_plan(problem):
    return [allocate_capacity(row, ceiling, budget)
            for row, ceiling, budget in zip(problem["demand"], problem["capacity"], problem["budget"])]


def oracle_reference(settings, actual, ceilings):
    problem = settings.problem(actual, ceilings, [0] * len(ceilings[0]))
    start = perf_counter()
    allocation = solve_allocation(problem)["allocation"]
    elapsed = perf_counter() - start
    return score_path(problem, allocation, actual), elapsed


def score_path(problem, allocation, actual):
    scores = evaluate_allocation(problem, allocation, realized_demand=[list(row) for row in actual])
    return {key: scores[key] for key in (*METRICS, "max_constraint_violation", "constraint_violations", "feasible")}


def paired_effect(differences, seed=8062):
    """Scenario-level paired bootstrap percentile interval with a fixed seed."""
    if len(differences) < 2:
        raise ValueError("at least two independent evaluation scenarios are needed")
    rng = Random(seed)
    size = len(differences)
    sampled = sorted(mean(rng.choices(differences, k=size)) for _ in range(2000))
    return {"n": size, "mean": mean(differences), "sd": stdev(differences),
            "bootstrap_95_percent": [sampled[49], sampled[1949]]}


def benchmark(forecast_doc, allocation_doc):
    config = ExperimentConfig.from_document(forecast_doc)
    settings = AllocationSettings.from_document(allocation_doc, len(config.locations))
    variants = {"heuristic_seasonal_mean": (Method.SEASONAL_MEAN, proportional_plan)}
    variants.update({f"lp_{method.value}": (method, lambda problem: solve_allocation(problem)["allocation"])
                     for method in Method})
    test_start = config.windows("test").start
    rows, timings = [], []
    for seed in config.seeds:
        panel, ceilings = synthetic_panel(config, seed)
        actual, local_limits = panel.demand[test_start:], ceilings[test_start:]
        oracle, elapsed = oracle_reference(settings, actual, local_limits)
        rows.append({"scenario_id": panel.scenario_id, "policy": "oracle_full_test", **oracle,
                     "forecast_mae": None, "forecast_rmse": None, "oracle_gap": 0.0})
        timings.append({"scenario_id": panel.scenario_id, "policy": "oracle_full_test",
                        "planning_seconds": elapsed, "decisions": 1})
        for name, (method, planner) in variants.items():
            initial = [0] * len(config.locations)
            previous = initial
            allocations, planned, errors = [], [], []
            seconds = 0.0
            for index in config.windows("test"):
                start = perf_counter()
                stop = index + config.horizon_days
                predicted = forecast_matrix(panel, index, config.horizon_days, method)
                problem = settings.problem(predicted, ceilings[index:stop], previous)
                allocation = planner(problem)
                seconds += perf_counter() - start
                planned.extend(predicted)
                allocations.extend(allocation)
                previous = allocation[-1]
                errors.extend(a - b for pred, truth in zip(predicted, panel.demand[index:stop])
                              for a, b in zip(pred, truth))
            scores = score_path(settings.problem(planned, local_limits, initial), allocations, actual)
            gap = scores["objective"] - oracle["objective"]
            if not scores["feasible"] or gap < -TOLERANCE:
                raise RuntimeError(f"failed feasibility or oracle check: {panel.scenario_id}, {name}")
            rows.append({"scenario_id": panel.scenario_id, "policy": name, **scores,
                         "forecast_mae": fsum(abs(error) for error in errors) / len(errors),
                         "forecast_rmse": sqrt(fsum(error * error for error in errors) / len(errors)),
                         "oracle_gap": gap})
            timings.append({"scenario_id": panel.scenario_id, "policy": name,
                            "planning_seconds": seconds, "decisions": len(config.windows("test"))})
    averages = {
        policy: {key: mean(row[key] for row in rows if row["policy"] == policy)
                 for key in (*METRICS, "oracle_gap")}
        for policy in ("oracle_full_test", *variants)
    }
    by_key = {(row["scenario_id"], row["policy"]): row for row in rows}
    pairs = {
        policy: paired_effect([
            by_key[f"seed-{seed}", policy]["objective"] - by_key[f"seed-{seed}", "lp_seasonal_mean"]["objective"]
            for seed in config.seeds
        ])
        for policy in ("heuristic_seasonal_mean", "lp_persistence", "lp_seasonal_naive")
    }
    return {"means": averages, "difference_vs_lp_seasonal_mean": pairs, "trajectories": rows}, timings

"""Deterministic, single-period allocation of divisible capacity."""

import argparse
import json
import math


def allocate_capacity(demand, capacity, budget):
    """Allocate in proportion to demand capped by each location's capacity.

    Inputs use the same divisible resource unit. Returns one allocation per
    location. This heuristic does not model costs, transfers, or integer units.
    """
    demand = [float(value) for value in demand]
    capacity = [float(value) for value in capacity]
    budget = float(budget)
    if not demand or len(demand) != len(capacity):
        raise ValueError("demand and capacity must have equal, nonzero lengths")
    if any(not math.isfinite(value) or value < 0
           for value in demand + capacity + [budget]):
        raise ValueError("all inputs must be finite and non-negative")

    eligible = [min(requested, limit)
                for requested, limit in zip(demand, capacity)]
    try:
        total = math.fsum(eligible)
    except OverflowError as error:
        raise ValueError("total eligible demand exceeds the numeric range") from error
    if total == 0:
        return [0.0] * len(demand)
    scale = min(1.0, budget / total)
    return [value * scale for value in eligible]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demand", nargs="+", type=float, required=True)
    parser.add_argument("--capacity", nargs="+", type=float, required=True)
    parser.add_argument("--budget", type=float, required=True)
    args = parser.parse_args()
    try:
        allocation = allocate_capacity(args.demand, args.capacity, args.budget)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps({
        "allocation": allocation,
        "unmet_demand": [max(0.0, requested - assigned)
                         for requested, assigned in zip(args.demand, allocation)],
        "unused_budget": max(0.0, args.budget - math.fsum(allocation)),
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

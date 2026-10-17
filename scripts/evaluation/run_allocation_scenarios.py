"""Evaluate the proportional baseline on versioned synthetic scenarios."""

import argparse
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tourism_control.optimization.proportional import allocate_capacity

FEASIBILITY_TOLERANCE = 1e-9


def evaluate_scenarios(document):
    """Return deterministic metrics; reject malformed or non-finite inputs."""
    if not isinstance(document, dict) or type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a nonempty list")
    rows = []
    seen = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("each scenario must be an object")
        name = scenario.get("id")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9_-]+", name) or name in seen:
            raise ValueError("scenario ids must be unique lowercase identifiers")
        seen.add(name)
        demand = scenario.get("demand")
        capacity = scenario.get("capacity")
        budget = scenario.get("budget")
        if not isinstance(demand, list) or not isinstance(capacity, list):
            raise ValueError(f"{name}: demand and capacity must be lists")
        if any(type(value) not in (int, float) for value in demand + capacity + [budget]):
            raise ValueError(f"{name}: inputs must be numeric, not strings or booleans")
        try:
            allocation = allocate_capacity(demand, capacity, budget)
            served = math.fsum(allocation)
            unmet = [max(0.0, requested - assigned)
                     for requested, assigned in zip(demand, allocation)]
            violation = max([0.0, served - budget]
                            + [-assigned for assigned in allocation]
                            + [assigned - min(requested, limit)
                               for assigned, requested, limit in zip(allocation, demand, capacity)])
            rows.append({
                "id": name,
                "allocation": allocation,
                "unmet_demand": unmet,
                "total_demand": math.fsum(demand),
                "total_served": served,
                "total_unmet": math.fsum(unmet),
                "unused_budget": max(0.0, budget - served),
                "max_constraint_violation": violation,
                "feasible": violation <= FEASIBILITY_TOLERANCE,
            })
        except (ValueError, OverflowError) as error:
            raise ValueError(f"{name}: invalid input or aggregate outside numeric range: {error}") from error
    return {
        "schema_version": 1,
        "method": "proportional_allocation",
        "feasibility_tolerance": FEASIBILITY_TOLERANCE,
        "all_feasible": all(row["feasible"] for row in rows),
        "results": rows,
    }


def as_markdown(report):
    lines = ["| Scenario | Served | Unmet demand | Unused budget | Feasible |",
             "|---|---:|---:|---:|:---:|"]
    for row in report["results"]:
        lines.append(f"| {row['id']} | {row['total_served']:.2f} | "
                     f"{row['total_unmet']:.2f} | {row['unused_budget']:.2f} | "
                     f"{'yes' if row['feasible'] else 'no'} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios", type=Path,
                        default=ROOT / "configs/optimization/allocation-scenarios.json")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    try:
        report = evaluate_scenarios(json.loads(args.scenarios.read_text(encoding="utf-8")))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, allow_nan=False) if args.format == "json"
          else as_markdown(report))
    return 0 if report["all_feasible"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

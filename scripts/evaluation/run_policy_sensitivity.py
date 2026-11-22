"""Compare fixed and optimization policies under one-at-a-time scenario changes."""

import argparse
from dataclasses import replace
from functools import partial
from pathlib import Path
from statistics import mean

from run_forecast_allocation import ALLOCATION_CONFIG, FORECAST_CONFIG, ROOT, read_json, write_results
from tourism_control.control.environment import ACTIONS, prepare_episode
from tourism_control.control.experiment import lp_policy, menu_policy, rollout
from tourism_control.forecasting.experiment import ExperimentConfig, synthetic_panel
from tourism_control.optimization.forecast_allocation import AllocationSettings, METRICS, paired_effect
from tourism_control.optimization.linear import validate_problem


def compare(forecast_doc, allocation_doc, control_doc, study):
    config = ExperimentConfig.from_document(forecast_doc)
    base = AllocationSettings.from_document(allocation_doc, len(config.locations))
    used = set(config.seeds)
    for key in ("training_scenario_seeds", "validation_scenario_seeds", "test_scenario_seeds"):
        used.update(control_doc[key])
    seeds = study["seeds"]
    if (type(study["schema_version"]) is not int or study["schema_version"] != 1
            or len(seeds) < 2 or any(type(seed) is not int or seed < 0 for seed in seeds)
            or len(set(seeds)) != len(seeds) or used.intersection(seeds)):
        raise ValueError("study requires disjoint, unique scenario seeds and schema version 1")

    def episode(seed):
        panel, ceilings = synthetic_panel(config, seed)
        return prepare_episode(panel, ceilings, config.windows("test").start, config.test_days,
                               control_doc["decision_lookahead_days"])

    episodes = [episode(seed) for seed in seeds]
    policies = {
        "proportional": partial(menu_policy, ACTIONS.index("proportional")),
        "priority_first": partial(menu_policy, ACTIONS.index("priority_first")),
        "receding_horizon_lp": lp_policy,
    }
    cases, rows, timings = {}, [], []
    for case, changes in study["cases"].items():
        if len(changes) > 1 or changes.keys() - {"budget_fraction", "unmet_penalty", "adjustment_cost"}:
            raise ValueError("cases change at most one declared study parameter")
        settings = replace(base, **changes)
        if type(settings.budget_fraction) not in (int, float) or not 0 < settings.budget_fraction <= 1:
            raise ValueError("budget_fraction must be in (0, 1]")
        limits = episodes[0].ceilings[:1]
        validate_problem(settings.problem(limits, limits, [0] * len(config.locations)))
        # This study has no oracle, so the oracle-specific cost restriction is unnecessary.
        outcomes = {name: [] for name in policies}
        for episode_data in episodes:
            for name, policy in policies.items():
                record, seconds = rollout(episode_data, settings, policy)
                rows.append({"case": case, "scenario_id": episode_data.scenario_id, "policy": name, **record})
                timings.append({"case": case, "scenario_id": episode_data.scenario_id, "policy": name,
                                "seconds": seconds, "decisions": len(episode_data.days)})
                outcomes[name].append(record)
        cases[case] = {
            "means": {name: {metric: mean(row[metric] for row in group) for metric in METRICS}
                      for name, group in outcomes.items()},
            "lp_minus_priority_objective": paired_effect([
                lp["objective"] - priority["objective"] for lp, priority in
                zip(outcomes["receding_horizon_lp"], outcomes["priority_first"])
            ]),
        }
    return {"study": study, "forecast": forecast_doc, "allocation": allocation_doc,
            "control": control_doc, "cases": cases, "trajectories": rows}, timings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, default=ROOT / "configs/control/policy-sensitivity.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report, timings = compare(
        read_json(FORECAST_CONFIG), read_json(ALLOCATION_CONFIG),
        read_json(ROOT / "configs/control/stage-e.json"), read_json(args.study),
    )
    write_results(args.output, report, timings)


if __name__ == "__main__":
    main()

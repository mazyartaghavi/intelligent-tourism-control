"""Paired evaluation of daily heuristic, LP and Q-learning decisions."""

from functools import partial
from math import isclose
from statistics import mean, stdev
from time import perf_counter

from tourism_control.forecasting.experiment import ExperimentConfig, synthetic_panel
from tourism_control.optimization.forecast_allocation import (
    AllocationSettings, METRICS, oracle_reference, paired_effect, score_path,
)
from tourism_control.optimization.linear import TOLERANCE, solve_allocation
from .environment import ACTIONS, DailyEnvironment, menu_allocations, prepare_episode
from .q_learning import state_key, train

PARTITIONS = ("training_scenario_seeds", "validation_scenario_seeds", "test_scenario_seeds")
TRAINING_PARAMETERS = ("passes", "alpha", "discount", "epsilon_start", "epsilon_end")


def validate_control(document, forecasting_seeds):
    fields = {"schema_version", "decision_lookahead_days", "learning_seeds",
              *PARTITIONS, *TRAINING_PARAMETERS}
    if not isinstance(document, dict) or set(document) != fields:
        raise ValueError("control configuration fields must match schema version 1")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("control schema_version must be 1")
    for name in (*PARTITIONS, "learning_seeds"):
        seeds = document[name]
        if (not isinstance(seeds, list) or len(seeds) < 2
                or any(type(seed) is not int or seed < 0 for seed in seeds)
                or len(set(seeds)) != len(seeds)):
            raise ValueError(f"{name} requires at least two distinct nonnegative integer seeds")
    used = set(forecasting_seeds)
    for partition in PARTITIONS:
        seeds = set(document[partition])
        if used & seeds:
            raise ValueError("scenario partitions and Stage A seeds must be disjoint")
        used.update(seeds)
    for name in ("decision_lookahead_days", "passes"):
        if type(document[name]) is not int or document[name] < 1:
            raise ValueError(f"{name} must be a positive integer")
    for name in ("alpha", "discount", "epsilon_start", "epsilon_end"):
        value = document[name]
        if type(value) not in (int, float) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be in [0, 1]")
    if document["alpha"] == 0 or document["epsilon_end"] > document["epsilon_start"]:
        raise ValueError("require positive alpha and nonincreasing epsilon")


def menu_policy(action, observation, settings):
    return menu_allocations(observation, settings)[action]


def lp_policy(observation, settings):
    problem = settings.problem(observation.demand_forecast, observation.ceilings, observation.previous)
    return solve_allocation(problem)["allocation"][0]


def learned_policy(policy, observation, settings):
    return menu_policy(policy.choose(state_key(observation, settings)), observation, settings)


def rollout(episode, settings, policy):
    env = DailyEnvironment(episode, settings)
    obs = env.reset()
    initial = obs.previous
    predicted, allocations, rewards = [], [], []
    seconds = 0.0
    while obs is not None:
        predicted.append(obs.demand_forecast[0])
        start = perf_counter()
        decision = policy(obs, settings)
        seconds += perf_counter() - start
        obs, reward, allocation = env.commit(decision)
        allocations.append(allocation)
        rewards.append(reward)
    scores = score_path(settings.problem(predicted, episode.ceilings, initial),
                        allocations, episode.actual)
    reward = sum(rewards)
    if not scores["feasible"] or not isclose(-reward, scores["objective"], rel_tol=0, abs_tol=TOLERANCE):
        raise RuntimeError(f"invalid realized rollout: {episode.scenario_id}")
    return {**scores, "cumulative_reward": reward}, seconds


def compare(forecast_doc, allocation_doc, control_doc):
    config = ExperimentConfig.from_document(forecast_doc)
    settings = AllocationSettings.from_document(allocation_doc, len(config.locations))
    validate_control(control_doc, config.seeds)
    lookahead = control_doc["decision_lookahead_days"]

    def episodes(partition):
        for seed in control_doc[partition]:
            panel, ceilings = synthetic_panel(config, seed)
            yield prepare_episode(panel, ceilings, config.windows("test").start, config.test_days, lookahead)

    fixed = {name: partial(menu_policy, action) for action, name in enumerate(ACTIONS)}
    validation = list(episodes("validation_scenario_seeds"))
    validation_scores = {
        name: mean(rollout(episode, settings, policy)[0]["objective"] for episode in validation)
        for name, policy in fixed.items()
    }
    selected = min(fixed, key=lambda name: (validation_scores[name], name))
    training = list(episodes("training_scenario_seeds"))
    timing, learning, learned = [], [], {}
    for seed in control_doc["learning_seeds"]:
        start = perf_counter()
        policy, steps = train(training, settings, seed, **{key: control_doc[key] for key in TRAINING_PARAMETERS})
        elapsed = perf_counter() - start
        key = f"q_{seed}"
        learned[key] = partial(learned_policy, policy)
        learning.append({"seed": seed, "transitions": steps, "table": policy.table()})
        timing.append({"phase": "training", "scenario_id": "", "policy": key,
                       "seconds": elapsed, "decisions": steps})

    rows = []
    evaluation = list(episodes("test_scenario_seeds"))
    for episode in evaluation:
        oracle, elapsed = oracle_reference(settings, episode.actual, episode.ceilings)
        rows.append({"scenario_id": episode.scenario_id, "policy": "oracle_full_test", **oracle,
                     "cumulative_reward": -oracle["objective"], "oracle_gap": 0.0})
        timing.append({"phase": "evaluation", "scenario_id": episode.scenario_id,
                       "policy": "oracle_full_test", "seconds": elapsed, "decisions": 1})
        for name, policy in {**fixed, "receding_horizon_lp": lp_policy, **learned}.items():
            metrics, seconds = rollout(episode, settings, policy)
            gap = metrics["objective"] - oracle["objective"]
            if gap < -TOLERANCE:
                raise RuntimeError("clairvoyant lower bound violated")
            rows.append({"scenario_id": episode.scenario_id, "policy": name, **metrics, "oracle_gap": gap})
            timing.append({"phase": "evaluation", "scenario_id": episode.scenario_id, "policy": name,
                           "seconds": seconds, "decisions": len(episode.days)})

    measures = (*METRICS, "oracle_gap", "cumulative_reward")
    names = ("oracle_full_test", *fixed, "receding_horizon_lp", *learned)
    averages = {
        name: {metric: mean(row[metric] for row in rows if row["policy"] == name) for metric in measures}
        for name in names
    }
    averages["q_mean"] = {metric: mean(averages[name][metric] for name in learned) for metric in measures}
    by_key = {(row["scenario_id"], row["policy"]): row["objective"] for row in rows}
    comparisons = {}
    for reference in sorted({selected, "proportional", "receding_horizon_lp"}):
        gaps = [mean(by_key[episode.scenario_id, name] for name in learned)
                - by_key[episode.scenario_id, reference] for episode in evaluation]
        comparisons[reference] = paired_effect(gaps)
    return {
        "selected_fixed_policy": selected, "validation_objective": validation_scores,
        "test_means": averages, "q_minus_reference_objective": comparisons,
        "q_seed_mean_objective_sd": stdev(averages[name]["objective"] for name in learned),
        "learning": learning, "trajectories": rows,
    }, timing

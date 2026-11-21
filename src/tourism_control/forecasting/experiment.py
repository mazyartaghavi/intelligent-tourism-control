"""Seeded demand scenarios and chronological baseline evaluation."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from math import fsum, sqrt
from random import Random

from .baselines import DemandHistory, Method, forecast, validate_identifier


@dataclass(frozen=True)
class ExperimentConfig:
    start: date
    locations: tuple[str, ...]
    training_days: int
    validation_days: int
    test_days: int
    horizon_days: int
    seeds: tuple[int, ...]

    @classmethod
    def from_document(cls, document: dict) -> "ExperimentConfig":
        if not isinstance(document, dict) or set(document) != {
            "schema_version", "start", "locations", "training_days",
            "validation_days", "test_days", "horizon_days", "seeds",
        }:
            raise ValueError("configuration fields must match schema version 1")
        if type(document["schema_version"]) is not int or document["schema_version"] != 1:
            raise ValueError("schema_version must be 1")
        try:
            start = date.fromisoformat(document["start"])
        except (ValueError, TypeError) as exc:
            raise ValueError("start must use YYYY-MM-DD") from exc
        if document["start"] != start.isoformat():
            raise ValueError("start must use YYYY-MM-DD")
        locations = document["locations"]
        seeds = document["seeds"]
        if not isinstance(locations, list) or not locations:
            raise ValueError("locations must be a nonempty list")
        for location in locations:
            validate_identifier(location)
        if len(set(locations)) != len(locations):
            raise ValueError("locations must be unique")
        if not isinstance(seeds, list) or not seeds or any(type(seed) is not int or seed < 0 for seed in seeds):
            raise ValueError("seeds must be nonnegative integers in a nonempty list")
        if len(set(seeds)) != len(seeds):
            raise ValueError("seeds must be unique")
        training, validation, test, horizon = (
            document[key] for key in ("training_days", "validation_days", "test_days", "horizon_days")
        )
        if any(type(count) is not int or count < 1 for count in (training, validation, test, horizon)):
            raise ValueError("partition lengths and horizon must be positive integers")
        if training < max(method.min_history_days for method in Method):
            raise ValueError("training must contain at least three weeks")
        if validation % horizon or test % horizon:
            raise ValueError("validation and test must contain whole forecast windows")
        if training + validation + test > (date.max - start).days:
            raise ValueError("configured dates exceed the supported calendar")
        return cls(start, tuple(locations), training, validation, test, horizon, tuple(seeds))

    @property
    def total_days(self) -> int:
        return self.training_days + self.validation_days + self.test_days

    def windows(self, split: str) -> range:
        if split == "validation":
            return range(self.training_days, self.training_days + self.validation_days, self.horizon_days)
        if split == "test":
            return range(self.training_days + self.validation_days, self.total_days, self.horizon_days)
        raise ValueError("split must be validation or test")


def synthetic_panel(config: ExperimentConfig, seed: int) -> tuple[DemandHistory, tuple[tuple[int, ...], ...]]:
    """Return synthetic requests and service ceilings for capacity-pressure diagnostics."""
    rng = Random(seed)
    weekday_effect = (-5, -5, -3, 0, 7, 17, 12)
    shock_starts = range(21, config.total_days, 28)
    shock_days = {
        start + rng.randrange(4): rng.choice((-18, 22))
        for start in shock_starts
    }
    demand = []
    ceilings = []
    common = 0.0
    for day in range(config.total_days):
        weekday = (config.start.weekday() + day) % 7
        common = 0.45 * common + rng.gauss(0, 4)
        shock = shock_days.get(day, 0) + 0.5 * shock_days.get(day - 1, 0)
        demand.append(tuple(
            max(0, round(36 + 9 * site + 0.11 * day
                         + (1 + 0.15 * site) * weekday_effect[weekday]
                         + common + shock + rng.gauss(0, 4 + site)))
            for site in range(len(config.locations))
        ))
        ceilings.append(tuple(
            57 + 10 * site - (8 if weekday >= 5 else 0)
            for site in range(len(config.locations))
        ))
    return DemandHistory(f"seed-{seed}", config.locations, config.start, tuple(demand)), tuple(ceilings)


def _scores(errors: list[float]) -> dict:
    if not errors:
        return {"n": 0, "mae": None, "rmse": None}
    return {
        "n": len(errors),
        "mae": fsum(abs(error) for error in errors) / len(errors),
        "rmse": sqrt(fsum(error * error for error in errors) / len(errors)),
    }


def evaluate(document: dict) -> tuple[dict, list[dict], list[dict]]:
    """Evaluate fixed methods on shared windows and select by validation MAE alone."""
    config = ExperimentConfig.from_document(document)
    scenarios = [synthetic_panel(config, seed) for seed in config.seeds]
    metrics = []
    per_scenario = []
    selected = None
    for split in ("validation", "test"):
        groups = defaultdict(list)
        for panel, ceilings in scenarios:
            scenario_errors = defaultdict(list)
            for index in config.windows(split):
                history = panel.before(config.start + timedelta(days=index))
                for method in Method:
                    for point in forecast(history, config.horizon_days, method):
                        day = index + point.horizon_days - 1
                        # Forecasts follow target/location order and are scored against that key.
                        column = config.locations.index(point.location_id)
                        actual = panel.demand[day][column]
                        error = point.predicted_demand - actual
                        groups[method.value, "all"].append(error)
                        groups[method.value, f"horizon_{point.horizon_days}"].append(error)
                        pressure = "above_capacity" if actual > ceilings[day][column] else "within_capacity"
                        groups[method.value, pressure].append(error)
                        scenario_errors[method.value].append(error)
            per_scenario.extend(
                {"split": split, "scenario_id": panel.scenario_id, "method": method.value,
                 **_scores(scenario_errors[method.value])}
                for method in Method
            )
        strata = ["all", *(f"horizon_{step}" for step in range(1, config.horizon_days + 1)),
                  "above_capacity", "within_capacity"]
        overall = {}
        for method in Method:
            for stratum in strata:
                scores = _scores(groups[method.value, stratum])
                metrics.append({"split": split, "method": method.value, "stratum": stratum, **scores})
                if stratum == "all":
                    overall[method.value] = scores
        if split == "validation":
            selected = min(overall, key=lambda candidate: (overall[candidate]["mae"], candidate))
    summary = {
        "schema_version": 1,
        "synthetic": True,
        "intervals_produced": False,
        "selected_by_validation_mae": selected,
        "configuration": document,
        "windows_per_scenario": {
            split: len(config.windows(split)) for split in ("validation", "test")
        },
        "overall_metrics": [row for row in metrics if row["stratum"] == "all"],
    }
    return summary, metrics, per_scenario

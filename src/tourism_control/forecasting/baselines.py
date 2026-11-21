"""Point forecasts for a regular panel of daily service requests."""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum
import re

DEMAND_UNIT = "service_requests_per_utc_day"
DAYS_PER_WEEK = 7
SEASONAL_WEEKS = 3


def validate_identifier(value: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", value):
        raise ValueError("expected a lowercase scenario or location identifier")


def validate_demand(value: float) -> None:
    if type(value) not in (int, float) or not 0 <= value < float("inf"):
        raise ValueError("demand must be finite and nonnegative")


@dataclass(frozen=True)
class DemandHistory:
    """Rows count requests during the UTC day starting at start + row index."""

    scenario_id: str
    locations: tuple[str, ...]
    start: date
    demand: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        validate_identifier(self.scenario_id)
        if type(self.start) is not date:
            raise ValueError("start must be a UTC calendar date")
        if not self.locations or not self.demand:
            raise ValueError("history requires locations and at least one day")
        for location in self.locations:
            validate_identifier(location)
        if len(set(self.locations)) != len(self.locations):
            raise ValueError("location identifiers must be unique")
        for row in self.demand:
            if len(row) != len(self.locations):
                raise ValueError("each day must contain a value for every location")
            for value in row:
                validate_demand(value)

    @property
    def end(self) -> date:
        """First day outside this history."""
        return self.start + timedelta(days=len(self.demand))

    def before(self, origin: date) -> "DemandHistory":
        """Select only observations from completed days at the forecast origin."""
        if type(origin) is not date or not self.start < origin <= self.end:
            raise ValueError("origin must follow the first day and cannot exceed history end")
        return DemandHistory(
            self.scenario_id, self.locations, self.start, self.demand[:(origin - self.start).days]
        )


class Method(str, Enum):
    PERSISTENCE = "persistence"
    SEASONAL_NAIVE = "seasonal_naive"
    SEASONAL_MEAN = "seasonal_mean"

    @property
    def min_history_days(self) -> int:
        if self is Method.PERSISTENCE:
            return 1
        if self is Method.SEASONAL_NAIVE:
            return DAYS_PER_WEEK
        return DAYS_PER_WEEK * SEASONAL_WEEKS


@dataclass(frozen=True)
class PredictionInterval:
    lower: float
    upper: float
    nominal_coverage: float

    def __post_init__(self) -> None:
        validate_demand(self.lower)
        validate_demand(self.upper)
        if self.lower > self.upper:
            raise ValueError("interval bounds must be ordered")
        if type(self.nominal_coverage) not in (int, float) or not 0 < self.nominal_coverage < 1:
            raise ValueError("nominal coverage must lie strictly between 0 and 1")


@dataclass(frozen=True)
class ForecastPoint:
    scenario_id: str
    location_id: str
    origin: date
    target: date
    horizon_days: int
    method: Method
    predicted_demand: float
    interval: PredictionInterval | None = None

    def __post_init__(self) -> None:
        validate_identifier(self.scenario_id)
        validate_identifier(self.location_id)
        validate_demand(self.predicted_demand)
        if type(self.origin) is not date or type(self.target) is not date:
            raise ValueError("origin and target must be UTC calendar dates")
        if type(self.horizon_days) is not int or self.horizon_days < 1:
            raise ValueError("horizon_days must be a positive integer")
        if (self.target - self.origin).days != self.horizon_days - 1:
            raise ValueError("target must equal origin plus horizon_days minus one day")
        if not isinstance(self.method, Method):
            raise ValueError("method must be a supported baseline")
        if self.interval is not None and not isinstance(self.interval, PredictionInterval):
            raise ValueError("interval must be a PredictionInterval or None")


def forecast(history: DemandHistory, horizon_days: int, method: Method) -> tuple[ForecastPoint, ...]:
    """Issue forecasts from completed-day history, ordered by target then location."""
    if type(horizon_days) is not int or horizon_days < 1:
        raise ValueError("horizon_days must be a positive integer")
    if not isinstance(method, Method):
        raise ValueError("method must be a supported baseline")
    if len(history.demand) < method.min_history_days:
        raise ValueError(f"{method.value} requires {method.min_history_days} days of history")

    origin = history.end
    predictions = []
    for offset in range(horizon_days):
        target = origin + timedelta(days=offset)
        for column, location in enumerate(history.locations):
            if method is Method.PERSISTENCE:
                predicted = history.demand[-1][column]
            else:
                phase = offset % DAYS_PER_WEEK
                weeks = 1 if method is Method.SEASONAL_NAIVE else SEASONAL_WEEKS
                predicted = sum(
                    history.demand[phase - week * DAYS_PER_WEEK][column] / weeks
                    for week in range(1, weeks + 1)
                )
            predictions.append(ForecastPoint(
                history.scenario_id, location, origin, target, offset + 1, method, predicted
            ))
    return tuple(predictions)

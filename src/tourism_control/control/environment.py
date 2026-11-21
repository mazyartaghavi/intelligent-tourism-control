"""Daily capacity commitments with forecast-only policy observations."""

from dataclasses import dataclass
from datetime import date, timedelta
from math import fsum, isfinite

from tourism_control.forecasting.baselines import Method
from tourism_control.optimization.forecast_allocation import forecast_matrix
from tourism_control.optimization.linear import TOLERANCE
from tourism_control.optimization.proportional import allocate_capacity

ACTIONS = ("proportional", "priority_first", "carry_then_fill", "blend")


@dataclass(frozen=True)
class Observation:
    day: date
    demand_forecast: tuple[tuple[float, ...], ...]
    ceilings: tuple[tuple[float, ...], ...]
    budgets: tuple[float, ...]
    previous: tuple[float, ...]


@dataclass(frozen=True)
class Episode:
    scenario_id: str
    days: tuple
    forecasts: tuple
    ceilings: tuple
    actual: tuple


def prepare_episode(panel, ceilings, start, days, lookahead):
    """Cache forecasts based on the completed history at each origin."""
    if not 0 < start < start + days <= len(panel.demand) or lookahead < 1:
        raise ValueError("episode dates must lie inside the panel and follow some history")
    stop = start + days
    return Episode(
        panel.scenario_id,
        tuple(panel.start + timedelta(days=index) for index in range(start, stop)),
        tuple(tuple(tuple(row) for row in forecast_matrix(
            panel, index, min(lookahead, stop - index), Method.SEASONAL_MEAN
        )) for index in range(start, stop)),
        tuple(ceilings[start:stop]),
        tuple(panel.demand[start:stop]),
    )


def menu_allocations(observation, settings):
    """Generate feasible candidates in deterministic action order."""
    ceilings = observation.ceilings[0]
    demand = observation.demand_forecast[0]
    budget = observation.budgets[0]
    upper = [min(requested, limit) for requested, limit in zip(demand, ceilings)]
    proportional = tuple(allocate_capacity(demand, ceilings, budget))
    order = sorted(range(len(upper)), key=lambda i: (settings.operating_cost[i] - settings.unmet_penalty[i], i))

    def fill(initial):
        chosen = list(initial)
        remaining = max(0.0, budget - fsum(chosen))
        for i in order:
            extra = min(max(0.0, upper[i] - chosen[i]), remaining)
            chosen[i] += extra
            remaining -= extra
        return tuple(chosen)

    priority = fill([0.0] * len(upper))
    carried = allocate_capacity(observation.previous, upper, budget)
    carry_then_fill = fill(carried)
    blend = tuple((a + b) / 2 for a, b in zip(proportional, priority))
    return proportional, priority, carry_then_fill, blend


class DailyEnvironment:
    """Reset to zero commitments, reveal each outcome after applying its action."""

    def __init__(self, episode, settings):
        self._episode = episode
        self.settings = settings
        self.reset()

    def reset(self):
        self._index = 0
        self._previous = (0.0,) * len(self._episode.ceilings[0])
        return self.observation()

    def observation(self):
        if self._index == len(self._episode.days):
            return None
        forecasts = self._episode.forecasts[self._index]
        ceilings = self._episode.ceilings[self._index:self._index + len(forecasts)]
        budgets = tuple(self.settings.budget_fraction * sum(row) for row in ceilings)
        return Observation(self._episode.days[self._index], forecasts, ceilings, budgets, self._previous)

    def step(self, action):
        obs = self.observation()
        if obs is None:
            raise ValueError("episode has ended")
        if type(action) is not int or not 0 <= action < len(ACTIONS):
            raise ValueError("action must be a valid candidate index")
        return self.commit(menu_allocations(obs, self.settings)[action])

    def commit(self, allocation):
        """Apply an allocation from any policy under the same hard constraints."""
        obs = self.observation()
        if obs is None:
            raise ValueError("episode has ended")
        chosen = tuple(float(value) for value in allocation)
        upper = tuple(min(a, b) for a, b in zip(obs.demand_forecast[0], obs.ceilings[0]))
        if (len(chosen) != len(upper)
                or any(not isfinite(x) or x < -TOLERANCE or x > limit + TOLERANCE
                       for x, limit in zip(chosen, upper))
                or fsum(chosen) > obs.budgets[0] + TOLERANCE):
            raise ValueError("allocation violates the forecast, site or shared budget constraints")
        actual = self._episode.actual[self._index]
        unmet = tuple(max(0.0, requested - assigned) for requested, assigned in zip(actual, chosen))
        weighted = fsum(p * u for p, u in zip(self.settings.unmet_penalty, unmet))
        operating = fsum(c * x for c, x in zip(self.settings.operating_cost, chosen))
        adjustment = fsum(k * abs(x - z) for k, x, z in zip(self.settings.adjustment_cost, chosen, self._previous))
        self._previous = chosen
        self._index += 1
        return self.observation(), -(weighted + operating + adjustment), chosen

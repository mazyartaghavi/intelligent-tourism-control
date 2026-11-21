"""Bounded tabular Q-learning over feasible capacity commitments."""

from collections import defaultdict
from math import fsum
from random import Random

from .environment import ACTIONS, DailyEnvironment, menu_allocations

PRIORITY = ACTIONS.index("priority_first")


def state_key(observation, settings):
    """Map public decision features to a small discrete state."""
    budget = observation.budgets[0]
    if budget == 0:
        return (observation.day.weekday() >= 5, 0, 0, False, 0)
    eligible = fsum(min(d, c) for d, c in zip(observation.demand_forecast[0], observation.ceilings[0]))
    priority = menu_allocations(observation, settings)[PRIORITY]
    change = fsum(abs(a - b) for a, b in zip(priority, observation.previous)) / budget
    largest_priority = max(range(len(priority)), key=lambda i: settings.unmet_penalty[i])
    change_up = priority[largest_priority] - observation.previous[largest_priority] > 0.1 * budget
    if len(observation.demand_forecast) == 1:
        next_load = 0
    else:
        difference = fsum(observation.demand_forecast[1]) - fsum(observation.demand_forecast[0])
        next_load = 2 if difference > 0.1 * budget else 1
    return (observation.day.weekday() >= 5, int(eligible > budget) + int(eligible > 1.4 * budget),
            int(change > 0.1) + int(change > 0.3), change_up, next_load)


class QPolicy:
    def __init__(self):
        self.values = defaultdict(lambda: [0.0] * len(ACTIONS))
        self.counts = defaultdict(lambda: [0] * len(ACTIONS))

    def choose(self, state):
        if state not in self.counts or not any(self.counts[state]):
            return PRIORITY
        return max((i for i, count in enumerate(self.counts[state]) if count),
                   key=lambda i: (self.values[state][i], i == PRIORITY, -i))

    def update(self, state, action, reward, next_state, alpha, discount):
        continuation = 0.0 if next_state is None else max(self.values[next_state])
        self.values[state][action] += alpha * (reward + discount * continuation - self.values[state][action])
        self.counts[state][action] += 1

    def table(self):
        return [{"state": list(key), "values": self.values[key], "visits": self.counts[key]}
                for key in sorted(self.counts)]


def train(episodes, settings, seed, passes, alpha, discount, epsilon_start, epsilon_end):
    policy = QPolicy()
    rng = Random(seed)
    total = len(episodes) * passes
    transitions = 0
    for run in range(passes):
        order = rng.sample(list(episodes), len(episodes))
        for index, episode in enumerate(order):
            progress = (run * len(order) + index) / max(1, total - 1)
            epsilon = epsilon_start + progress * (epsilon_end - epsilon_start)
            env = DailyEnvironment(episode, settings)
            obs = env.reset()
            while obs is not None:
                state = state_key(obs, settings)
                action = rng.randrange(len(ACTIONS)) if rng.random() < epsilon else policy.choose(state)
                obs, reward, _ = env.step(action)
                following = None if obs is None else state_key(obs, settings)
                policy.update(state, action, reward, following, alpha, discount)
                transitions += 1
    return policy, transitions

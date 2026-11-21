import json
from dataclasses import replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from tourism_control.control.environment import ACTIONS, DailyEnvironment, prepare_episode
from tourism_control.forecasting.experiment import ExperimentConfig, synthetic_panel
from tourism_control.optimization.forecast_allocation import AllocationSettings, score_path


def fixture():
    forecast = json.loads((ROOT / "configs/forecasting/stage-a.json").read_text(encoding="utf-8"))
    costs = json.loads((ROOT / "configs/optimization/forecast-allocation.json").read_text(encoding="utf-8"))
    config = ExperimentConfig.from_document(forecast)
    settings = AllocationSettings.from_document(costs, len(config.locations))
    panel, ceilings = synthetic_panel(config, 5270)
    return panel, ceilings, settings


class DailyEnvironmentTests(unittest.TestCase):
    def test_reward_matches_realized_scoring_for_every_action(self):
        panel, ceilings, settings = fixture()
        episode = prepare_episode(panel, ceilings, 98, 7, 7)
        for action in range(len(ACTIONS)):
            env = DailyEnvironment(episode, settings)
            obs = env.reset()
            allocations, predicted, rewards = [], [], []
            while obs is not None:
                predicted.append(obs.demand_forecast[0])
                obs, reward, allocation = env.step(action)
                allocations.append(allocation)
                rewards.append(reward)
            problem = settings.problem(predicted, episode.ceilings, (0, 0, 0))
            result = score_path(problem, allocations, episode.actual)
            self.assertTrue(result["feasible"])
            self.assertAlmostEqual(-sum(rewards), result["objective"])
            with self.assertRaises(ValueError):
                env.step(action)
            self.assertEqual(env.reset().previous, (0, 0, 0))

    def test_future_demand_does_not_enter_observation(self):
        panel, ceilings, settings = fixture()
        shift = replace(panel, demand=panel.demand[:98] + ((500, 500, 500),) * 42)
        original = DailyEnvironment(prepare_episode(panel, ceilings, 98, 7, 7), settings)
        changed = DailyEnvironment(prepare_episode(shift, ceilings, 98, 7, 7), settings)
        self.assertEqual(original.observation(), changed.observation())
        self.assertNotEqual(original.step(0)[1], changed.step(0)[1])

    def test_invalid_commitment_is_rejected_without_advancing(self):
        panel, ceilings, settings = fixture()
        env = DailyEnvironment(prepare_episode(panel, ceilings, 98, 7, 7), settings)
        first = env.observation()
        for allocation in ((-1, 0, 0), (float("nan"), 0, 0), (200, 200, 200), (0,)):
            with self.assertRaises(ValueError):
                env.commit(allocation)
            self.assertEqual(env.observation(), first)

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from test_daily_environment import fixture
from tourism_control.control.environment import prepare_episode
from tourism_control.control.q_learning import PRIORITY, QPolicy, train


class QLearningTests(unittest.TestCase):
    def test_update_for_terminal_and_continuing_transitions(self):
        policy = QPolicy()
        a, b = ("before",), ("after",)
        self.assertEqual(policy.choose(b), PRIORITY)
        policy.update(b, 0, -3.0, None, 1.0, 0.8)
        self.assertEqual(policy.choose(b), 0)
        for action in (1, 2, 3):
            policy.update(b, action, -5.0, None, 1.0, 0.8)
        policy.update(a, 1, -2.0, b, 0.5, 0.8)
        self.assertAlmostEqual(policy.values[a][1], -2.2)

    def test_training_reproduces_policy_and_update_count(self):
        panel, ceilings, settings = fixture()
        episodes = [prepare_episode(panel, ceilings, 98, 7, 7)]
        arguments = dict(seed=101, passes=3, alpha=0.2, discount=0.97, epsilon_start=0.4, epsilon_end=0.1)
        first, steps = train(episodes, settings, **arguments)
        second, repeated = train(episodes, settings, **arguments)
        self.assertEqual(steps, 21)
        self.assertEqual(steps, repeated)
        self.assertEqual(first.table(), second.table())

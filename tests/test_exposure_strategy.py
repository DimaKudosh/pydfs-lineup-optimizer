import unittest
from pydfs_lineup_optimizer.exposure_strategy import TotalExposureStrategy, AfterEachExposureStrategy


class ExposureStrategyTestCase(unittest.TestCase):
    def test_total_exposure(self):
        strategy = TotalExposureStrategy({
            'a': 0.5,
            'b': 0.25,
            'c': 0.75,
        }, 4)
        strategy.set_used(['a', 'b', 'c'])
        self.assertFalse(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertFalse(strategy.is_reached_exposure('c'))
        strategy.set_used(['a', 'b', 'c'])
        self.assertTrue(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertFalse(strategy.is_reached_exposure('c'))
        strategy.set_used(['a', 'b', 'c'])
        self.assertTrue(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertTrue(strategy.is_reached_exposure('c'))

    def test_after_each_exposure(self):
        strategy = AfterEachExposureStrategy({
            'a': 0.5,
            'b': 0.25,
            'c': 0.75,
        }, 4)
        strategy.set_used(['a', 'b', 'c'])
        self.assertTrue(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertTrue(strategy.is_reached_exposure('c'))
        strategy.set_used([])
        self.assertTrue(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertFalse(strategy.is_reached_exposure('c'))
        strategy.set_used([])
        self.assertFalse(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertFalse(strategy.is_reached_exposure('c'))
        strategy.set_used(['a', 'b', 'c'])
        self.assertTrue(strategy.is_reached_exposure('a'))
        self.assertTrue(strategy.is_reached_exposure('b'))
        self.assertFalse(strategy.is_reached_exposure('c'))

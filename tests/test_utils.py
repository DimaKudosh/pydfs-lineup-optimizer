import unittest
from functools import partial
from pydfs_lineup_optimizer import settings
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.settings import LineupPosition
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.utils import ratio, get_positions_for_optimizer, link_players_with_positions, \
    list_intersection, process_percents
from pydfs_lineup_optimizer.sites.draftkings.classic.settings import DraftKingsBasketballSettings, \
    DraftKingsFootballSettings, DraftKingsBaseballSettings, DraftKingsHockeySettings
from pydfs_lineup_optimizer.tz import get_timezone, set_timezone
from .utils import create_players


class UtilsTestCase(unittest.TestCase):
    def test_ratio(self):
        threshold = 0.8
        self.assertTrue(ratio('Blake Griffin', 'Blake Griffin') >= threshold)
        self.assertTrue(ratio('griffin', 'Blake Griffin') >= threshold)
        self.assertTrue(ratio('grifin', 'Blake Griffin') >= threshold)
        self.assertFalse(ratio('Hood', 'Blake Griffin') >= threshold)

    def test_list_intersection(self):
        self.assertTrue(list_intersection(['PG'], ['SG', 'PG']))
        self.assertTrue(list_intersection(['SG', 'PG'], ['PG']))
        self.assertFalse(list_intersection(['PG'], ['SF', 'PF']))

    def test_process_percents(self):
        self.assertIsNone(process_percents(None))
        self.assertEqual(process_percents(0.3), 0.3)
        self.assertEqual(process_percents(30), 0.3)


class PositionsConverterTestCase(unittest.TestCase):
    class TestSettings(settings.BaseSettings):
        positions = [
            LineupPosition('1', ('1',)),
            LineupPosition('2', ('2',)),
            LineupPosition('3', ('3',)),
            LineupPosition('23', ('2', '3')),
            LineupPosition('23', ('2', '3')),
            LineupPosition('all', ('1', '2', '3')),
            LineupPosition('all', ('1', '2', '3')),
        ]

    def test_optimizer_positions_processing(self):
        optimizer = LineupOptimizer(self.TestSettings)
        positions = get_positions_for_optimizer(optimizer.settings.positions)
        self.assertEqual(len(positions), 5)
        self.assertEqual(positions[('1', )], 1)
        self.assertEqual(positions[('2', )], 1)
        self.assertEqual(positions[('3', )], 1)
        self.assertEqual(positions[('2', '3')], 4)
        self.assertEqual(positions[('1', '2', '3')], 7)

    def test_optimizer_positions_processing_with_multipositions(self):
        optimizer = LineupOptimizer(self.TestSettings)
        positions = get_positions_for_optimizer(
            optimizer.settings.positions, {('1', '2'), ('2', '3'), ('1', '3')})
        self.assertEqual(len(positions), 7)
        self.assertEqual(positions[('1',)], 1)
        self.assertEqual(positions[('2',)], 1)
        self.assertEqual(positions[('3',)], 1)
        self.assertEqual(positions[('2', '3')], 4)
        self.assertEqual(positions[('1', '2')], 2)
        self.assertEqual(positions[('1', '3')], 2)
        self.assertEqual(positions[('1', '2', '3')], 7)


class LineupBuildingTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.link_nba_positions = partial(link_players_with_positions, positions=DraftKingsBasketballSettings.positions)
        cls.link_nfl_positions = partial(link_players_with_positions, positions=DraftKingsFootballSettings.positions)
        cls.link_mlb_positions = partial(link_players_with_positions, positions=DraftKingsBaseballSettings.positions)
        cls.link_nhl_positions = partial(link_players_with_positions, positions=DraftKingsHockeySettings.positions)

    def test_basketball_lineup_building_correct(self):
        self.link_nba_positions(create_players(['PG', 'SG', 'SF', 'PF', 'C', 'SG', 'SF', 'SF']))
        # Test different combinations of multi-positional players
        self.link_nba_positions(create_players(['PG/SG', 'SG/SF', 'SF/PF', 'PF/C', 'C/PG', 'SG/SF', 'SF/PF', 'SF/PF']))
        self.link_nba_positions(create_players(['PG', 'PG', 'C', 'C', 'SG/SF', 'SF/PF', 'SF/PF', 'PG/SG']))
        self.link_nba_positions(create_players(['C', 'SG/SF', 'PG/SG', 'SG/SF', 'SG/SF', 'C', 'SF/PF', 'PG']))
        self.link_nba_positions(create_players(['SG', 'PF', 'C', 'C', 'PF', 'PG/SF', 'PG/SG', 'PG/SG']))
        self.link_nba_positions(create_players(['PG', 'PG/SG', 'PG/SG/SF', 'PG/SF/PF', 'PG/PF/C', 'PG', 'PG/SF/PF',
                                                'PG/SG']))

    def test_basketball_lineup_building_incorrect(self):
        with self.assertRaises(LineupOptimizerException):
            # 3 C can't be linked
            self.link_nba_positions(create_players(['PG', 'SG', 'SF', 'PF', 'C', 'SG', 'C', 'C']))

    def test_football_lineup_building_correct(self):
        self.link_nfl_positions(create_players(['QB', 'WR', 'WR', 'WR', 'WR', 'RB', 'RB', 'TE', 'DST']))

    def test_football_lineup_building_incorrect(self):
        with self.assertRaises(LineupOptimizerException):
            # Lineup hasn't defense
            self.link_nfl_positions(create_players(['QB', 'WR', 'WR', 'WR', 'WR', 'WR', 'RB', 'RB', 'TE']))

    def test_hockey_lineup_building_correct(self):
        self.link_nhl_positions(create_players(['LW', 'RW', 'LW', 'RW', 'C', 'C', 'D', 'D', 'G']))

    def test_hockey_lineup_building_incorrect(self):
        with self.assertRaises(LineupOptimizerException):
            # Should be 2 C
            self.link_nhl_positions(create_players(['LW', 'RW', 'LW', 'RW', 'LW', 'C', 'D', 'D', 'G']))

    def test_baseball_lineup_building_correct(self):
        self.link_mlb_positions(create_players(['SP', 'SP', 'C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']))

    def test_baseball_lineup_building_incorrect(self):
        with self.assertRaises(LineupOptimizerException):
            # Should be 2 P
            self.link_mlb_positions(create_players(['SP', 'C', 'C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']))


class TZTestCase(unittest.TestCase):
    def setUp(self):
        self.default_tz = get_timezone()

    def tearDown(self):
        set_timezone(self.default_tz)

    def test_change_tz(self):
        new_tz = 'UTC'
        set_timezone(new_tz)
        self.assertEqual(get_timezone(), new_tz)

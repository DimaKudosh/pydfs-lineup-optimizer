from __future__ import absolute_import, division
import unittest
from pydfs_lineup_optimizer import settings, Player
from pydfs_lineup_optimizer import get_optimizer
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.settings import LineupPosition
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.utils import ratio
from pydfs_lineup_optimizer.sites.yahoo.settings import YahooFootballSettings
from utils import create_players, load_players


class OptimizerMethodsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.players = load_players()

    def setUp(self):
        self.lineup_optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        self.lineup_optimizer.load_players(self.players[:])

    def test_optimizer_positions_processing(self):
        class TestSettings(settings.BaseSettings):
            positions = [
                LineupPosition('1', ('1', )),
                LineupPosition('2', ('2', )),
                LineupPosition('3', ('3', )),
                LineupPosition('23', ('2', '3')),
                LineupPosition('23', ('2', '3')),
                LineupPosition('all', ('1', '2', '3')),
                LineupPosition('all', ('1', '2', '3')),
            ]
        optimizer = LineupOptimizer(TestSettings)
        positions = optimizer.get_positions_for_optimizer()
        self.assertEqual(len(positions), 7)
        self.assertEqual(positions[('1', )], 1)
        self.assertEqual(positions[('2', )], 1)
        self.assertEqual(positions[('3', )], 1)
        self.assertEqual(positions[('2', '3')], 4)
        self.assertEqual(positions[('1', '2')], 2)
        self.assertEqual(positions[('1', '3')], 2)
        self.assertEqual(positions[('1', '2', '3')], 7)

    def test_add_player_to_lineup(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.add_player_to_lineup(self.players[0])
        self.assertTrue(self.players[0] in self.lineup_optimizer.locked_players)

    def test_same_players_in_lineup(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.add_player_to_lineup(self.players[0])
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(self.players[0])

    def test_add_player_with_many_positions(self):
        players = create_players(['PG/SG', 'PG', 'PG', 'PG', 'PG/SG/SF', 'SF', 'SF'])
        self.lineup_optimizer.extend_players(players)
        self.lineup_optimizer.add_player_to_lineup(players[0])
        self.lineup_optimizer.add_player_to_lineup(players[1])
        self.lineup_optimizer.add_player_to_lineup(players[2])
        self.lineup_optimizer.add_player_to_lineup(players[3])
        lineup = next(self.lineup_optimizer.optimize(1))
        self.assertTrue(all([p in lineup.players for p in players[:4]]))
        self.lineup_optimizer.add_player_to_lineup(players[4])
        lineup = next(self.lineup_optimizer.optimize(1))
        self.assertTrue(all([p in lineup.players for p in players[:5]]))
        num_of_selected_by_optimizer = len(list(filter(
            lambda p: 'C' in p.positions or 'PF' in p.positions, lineup.players
        )))
        self.assertEqual(num_of_selected_by_optimizer, 2)

    def test_exact_number_of_players_for_position(self):
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL)
        positions = ['OF', 'OF', '2B', '3B', 'SP', 'OF/SS', 'SP', '1B/OF', 'C', 'RP']
        optimizer.load_players(create_players(positions))
        with self.assertRaises(LineupOptimizerException):
            next(optimizer.optimize(1))
        positions.append('1B')
        optimizer.load_players(create_players(positions))
        next(optimizer.optimize(1))

    def test_adding_player_with_salary_bigger_than_budget(self):
        self.lineup_optimizer.reset_lineup()
        player = Player(1, '1', '1', ['PG'], 'DEN', 100000, 2)
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(player)

    def test_adding_player_to_formed_position(self):
        self.lineup_optimizer.reset_lineup()
        players = []
        for i in '1234':
            players.append(Player(int(i), i, i, ['PG'], 'DEN', 10, 2))
        for i in range(3):
            self.lineup_optimizer.add_player_to_lineup(players[i])
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(players[3])

    def test_remove_player_from_lineup(self):
        optimizer = self.lineup_optimizer
        optimizer.reset_lineup()
        player = Player(1, 'P', 'P', ['PG'], 'DEN', 10, 2)
        optimizer.extend_players([player])
        optimizer.add_player_to_lineup(player)
        optimizer.remove_player_from_lineup(player)
        self.assertNotIn(player, optimizer.locked_players)
        with self.assertRaises(LineupOptimizerException):
            optimizer.remove_player_from_lineup(player)

    def test_lineup_with_max_players(self):
        self.lineup_optimizer.reset_lineup()
        players = [Player(1, 'P1', 'P1', ['PG'], 'DEN', 10, 2), Player(5, 'P5', 'P5', ['SG'], 'DEN', 10, 2),
                   Player(2, 'P2', 'P2', ['SF'], 'DEN', 10, 2), Player(6, 'P6', 'P6', ['PF'], 'DEN', 10, 2),
                   Player(3, 'P3', 'P3', ['C'], 'DEN', 10, 2), Player(7, 'P7', 'P7', ['PG'], 'DEN', 10, 2),
                   Player(4, 'P4', 'P4', ['PF'], 'DEN', 10, 2), Player(8, 'P8', 'P8', ['PG'], 'DEN', 10, 2)]
        self.lineup_optimizer.extend_players(players)
        for player in players:
            self.lineup_optimizer.add_player_to_lineup(player)
        gen = self.lineup_optimizer.optimize(10)
        self.assertEqual(len(list(gen)), 1)

    def test_get_optimizer(self):
        optimizer = get_optimizer(Site.YAHOO, Sport.FOOTBALL)
        self.assertEqual(optimizer._settings, YahooFootballSettings)
        with self.assertRaises(NotImplementedError):
            get_optimizer(Site.DRAFTKINGS, 'Some sport')

    def test_ratio(self):
        threshold = 0.8
        self.assertTrue(ratio('Blake Griffin', 'Blake Griffin') >= threshold)
        self.assertTrue(ratio('griffin', 'Blake Griffin') >= threshold)
        self.assertTrue(ratio('grifin', 'Blake Griffin') >= threshold)
        self.assertFalse(ratio('Hood', 'Blake Griffin') >= threshold)

    def test_lineup_building(self):
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        optimizer._build_lineup(create_players(['PG', 'SG', 'SF', 'PF', 'C', 'SG', 'SF', 'SF']))
        optimizer._build_lineup(create_players(['PG/SG', 'SG/SF', 'SF/PF', 'PF/C', 'C/PG', 'SG/SF', 'SF/PF', 'SF/PF']))
        optimizer._build_lineup(create_players(['PG', 'PG', 'C', 'C', 'SG/SF', 'SF/PF', 'SF/PF', 'PG/SG']))
        optimizer._build_lineup(create_players(['C', 'SG/SF', 'PG/SG', 'SG/SF', 'SG/SF', 'C', 'SF/PF', 'PG']))
        optimizer._build_lineup(create_players(['SG', 'PF', 'C', 'C', 'PF', 'PG/SF', 'PG/SG', 'PG/SG']))
        optimizer._build_lineup(create_players(['PG', 'PG/SG', 'PG/SG/SF', 'PG/SF/PF', 'PG/PF/C', 'PG', 'PG/SF/PF',
                                                'PG/SG']))
        with self.assertRaises(LineupOptimizerException):
            optimizer._build_lineup(create_players(['PG', 'SG', 'SF', 'PF', 'C', 'SG', 'C', 'C']))
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.FOOTBALL)
        optimizer._build_lineup(create_players(['QB', 'WR', 'WR', 'WR', 'WR', 'RB', 'RB', 'TE', 'DST']))
        with self.assertRaises(LineupOptimizerException):
            optimizer._build_lineup(create_players(['QB', 'WR', 'WR', 'WR', 'WR', 'WR', 'RB', 'RB', 'TE']))
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.HOCKEY)
        optimizer._build_lineup(create_players(['LW', 'RW', 'LW', 'RW', 'C', 'C', 'D', 'D', 'G']))
        with self.assertRaises(LineupOptimizerException):
            optimizer._build_lineup(create_players(['LW', 'RW', 'LW', 'RW', 'LW', 'C', 'D', 'D', 'G']))
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL)
        optimizer._build_lineup(create_players(['SP', 'SP', 'C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']))
        with self.assertRaises(LineupOptimizerException):
            optimizer._build_lineup(create_players(['P', 'C', 'C', '1B', '2B', '3B', 'SS', 'OF', 'OF', 'OF']))
        optimizer = get_optimizer(Site.FANTASY_DRAFT, Sport.BASKETBALL)
        optimizer._build_lineup(create_players(['PG', 'PG', 'PG', 'SF', 'SF', 'SF', 'SF', 'SF']))
        with self.assertRaises(LineupOptimizerException):
            optimizer._build_lineup(create_players(['PG', 'PG', 'SF', 'SF', 'SF', 'SF', 'SF', 'SF']))

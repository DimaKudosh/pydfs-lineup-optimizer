from __future__ import absolute_import, division
import unittest
from pydfs_lineup_optimizer import get_optimizer, Player
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.sites.yahoo.settings import YahooFootballSettings
from .utils import create_players, load_players


class OptimizerMethodsTestCase(unittest.TestCase):
    def setUp(self):
        self.players = load_players()
        self.lineup_optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        self.lineup_optimizer.load_players(self.players)

    def test_add_player_to_lineup(self):
        self.lineup_optimizer.add_player_to_lineup(self.players[0])
        self.assertTrue(self.players[0] in self.lineup_optimizer.locked_players)

    def test_same_players_in_lineup(self):
        self.lineup_optimizer.add_player_to_lineup(self.players[0])
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(self.players[0])

    def test_add_player_with_many_positions(self):
        players = create_players(['PG/SG', 'PG', 'PG', 'PG', 'PG/SG/SF', 'SF', 'SF'])
        self.lineup_optimizer.extend_players(players)
        for player in players[:4]:
            self.lineup_optimizer.add_player_to_lineup(player)
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
        player = Player('1', '1', '1', ['PG'], 'DEN', 100000, 2)
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(player)

    def test_adding_player_to_formed_position(self):
        players = create_players(['PG'] * 4)
        for i in range(3):
            self.lineup_optimizer.add_player_to_lineup(players[i])
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(players[3])

    def test_remove_player_from_lineup(self):
        optimizer = self.lineup_optimizer
        player = Player('1', 'P', 'P', ['PG'], 'DEN', 10, 2)
        optimizer.extend_players([player])
        optimizer.add_player_to_lineup(player)
        optimizer.remove_player_from_lineup(player)
        self.assertNotIn(player, optimizer.locked_players)
        with self.assertRaises(LineupOptimizerException):
            optimizer.remove_player_from_lineup(player)

    def test_lineup_with_max_players(self):
        players = create_players(['PG', 'SG', 'SF', 'PF', 'C', 'PG', 'SF', 'C'])
        self.lineup_optimizer.extend_players(players)
        for player in players:
            self.lineup_optimizer.add_player_to_lineup(player)
        gen = self.lineup_optimizer.optimize(10)
        self.assertEqual(len(list(gen)), 1)

    def test_get_optimizer(self):
        optimizer = get_optimizer(Site.YAHOO, Sport.FOOTBALL)
        self.assertIsInstance(optimizer._settings, YahooFootballSettings)
        with self.assertRaises(NotImplementedError):
            get_optimizer(Site.DRAFTKINGS, 'Some sport')

    def test_get_player_by_id(self):
        player = self.lineup_optimizer.get_player_by_id('0000001')
        self.assertIsNotNone(player)
        self.assertEqual(player.last_name, 'Westbrook')

    def test_get_player_by_incorrect_id(self):
        player = self.lineup_optimizer.get_player_by_id('incorrect_id')
        self.assertIsNone(player)

    def test_print_stats_before_optimization(self):
        optimizer = get_optimizer(Site.YAHOO, Sport.FOOTBALL)
        with self.assertRaises(LineupOptimizerException):
            optimizer.print_statistic()

    def test_export_before_optimization(self):
        optimizer = get_optimizer(Site.YAHOO, Sport.FOOTBALL)
        with self.assertRaises(LineupOptimizerException):
            optimizer.export('temp.csv')

import unittest
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup, LineupPlayer
from pydfs_lineup_optimizer.fantasy_points_strategy import StandardFantasyPointsStrategy, \
    RandomFantasyPointsStrategy, ProgressiveFantasyPointsStrategy


class FantasyPointsStrategyTestCase(unittest.TestCase):
    def test_standard_strategy(self):
        player1 = Player('1', '1', '1', ['P'], 'test', 5000, 20)
        player2 = Player('2', '2', '2', ['P'], 'test', 8000, 30)
        strategy = StandardFantasyPointsStrategy()
        self.assertEqual(strategy.get_player_fantasy_points(player1), 20)
        self.assertEqual(strategy.get_player_fantasy_points(player2), 30)
        strategy.set_previous_lineup(Lineup([LineupPlayer(player1, 'P')]))
        self.assertEqual(strategy.get_player_fantasy_points(player1), 20)
        self.assertEqual(strategy.get_player_fantasy_points(player2), 30)

    def test_random_strategy(self):
        player1 = Player('1', '1', '1', ['P'], 'test', 5000, 20, min_deviation=0.1, max_deviation=0.2)
        player2 = Player('2', '2', '2', ['P'], 'test', 8000, 40)
        strategy = RandomFantasyPointsStrategy(0.05, 0.1)
        player1_fppg = strategy.get_player_fantasy_points(player1)
        if player1_fppg < 16 or 18 < player1_fppg < 22 or player1_fppg > 24:
            self.fail('Incorrect generated points')
        player2_fppg = strategy.get_player_fantasy_points(player2)
        if player2_fppg < 36 or 38 < player2_fppg < 42 or player2_fppg > 44:
            self.fail('Incorrect generated points')
        strategy.set_previous_lineup(Lineup([LineupPlayer(player1, 'P')]))
        player1_fppg = strategy.get_player_fantasy_points(player1)
        if player1_fppg < 16 or 18 < player1_fppg < 22 or player1_fppg > 24:
            self.fail('Incorrect generated points')
        player2_fppg = strategy.get_player_fantasy_points(player2)
        if player2_fppg < 36 or 38 < player2_fppg < 42 or player2_fppg > 44:
            self.fail('Incorrect generated points')

    def test_progressive_strategy(self):
        player1 = Player('1', '1', '1', ['P'], 'test', 5000, 20)
        player2 = Player('2', '2', '2', ['P'], 'test', 8000, 30, progressive_scale=0.2)
        strategy = ProgressiveFantasyPointsStrategy(scale=0.1)
        self.assertEqual(strategy.get_player_fantasy_points(player1), 20)
        self.assertEqual(strategy.get_player_fantasy_points(player2), 30)
        strategy.set_previous_lineup(Lineup([LineupPlayer(player1, 'P')]))
        self.assertEqual(strategy.get_player_fantasy_points(player1), 20)
        self.assertEqual(strategy.get_player_fantasy_points(player2), 36)
        strategy.set_previous_lineup(Lineup([LineupPlayer(player1, 'P')]))
        self.assertEqual(strategy.get_player_fantasy_points(player1), 20)
        self.assertEqual(strategy.get_player_fantasy_points(player2), 42)
        strategy.set_previous_lineup(Lineup([LineupPlayer(player2, 'P')]))
        self.assertEqual(strategy.get_player_fantasy_points(player1), 22)
        self.assertEqual(strategy.get_player_fantasy_points(player2), 30)

import unittest
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer import settings
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.utils import ratio


class TestLineupOptimizer(unittest.TestCase):
    def setUp(self):
        self.lineup_optimizer = LineupOptimizer(settings.YahooBasketballSettings)
        self.lineup_optimizer.load_players_from_CSV("tests/yahoo_dfs_test_sample.csv")
        self._player1 = self.lineup_optimizer._players[0]

    def test_add_player_to_lineup(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.add_player_to_lineup(self._player1)
        self.assertTrue(self._player1 in self.lineup_optimizer._lineup)

    def test_same_players_in_lineup(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.add_player_to_lineup(self._player1)
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(self._player1)

    def test_adding_player_with_salary_bigger_than_budget(self):
        self.lineup_optimizer.reset_lineup()
        player = Player('', '', '', ['PG'], 'DEN', 100000, 2)
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(player)

    def test_adding_player_to_formed_position(self):
        self.lineup_optimizer.reset_lineup()
        players = []
        for i in 'abcd':
            players.append(Player(i, i, i, ['PG'], 'DEN', 10, 2))
        for i in range(3):
            self.lineup_optimizer.add_player_to_lineup(players[i])
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(players[3])

    def test_remove_player_from_lineup(self):
        self.lineup_optimizer.reset_lineup()
        player1 = Player('', 'P', 'P', ['PG'], 'DEN', 10, 2)
        player2 = Player('', 'C', 'C', ['PG'], 'DEN', 10, 2)
        player3 = Player('', 'P', 'P', ['PG'], 'DEN', 10, 2)
        self.lineup_optimizer.add_player_to_lineup(player1)
        self.lineup_optimizer.remove_player_from_lineup(player1)
        self.assertEqual(len(self.lineup_optimizer._lineup), 0)
        self.lineup_optimizer.add_player_to_lineup(player1)
        self.lineup_optimizer.add_player_to_lineup(player2)
        self.lineup_optimizer.add_player_to_lineup(player3)
        self.lineup_optimizer.remove_player_from_lineup(player1)
        self.assertEqual(self.lineup_optimizer._positions[('PG', )], 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')], 1)
        self.assertEqual(self.lineup_optimizer._no_position_players, 1)
        self.lineup_optimizer.remove_player_from_lineup(player2)
        self.assertEqual(self.lineup_optimizer._positions[('PG', )], 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')], 2)
        self.assertEqual(self.lineup_optimizer._no_position_players, 1)
        self.lineup_optimizer.remove_player_from_lineup(player3)
        self.assertEqual(self.lineup_optimizer._positions[('PG', )], 1)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')], 3)
        self.assertEqual(self.lineup_optimizer._no_position_players, 1)

    def test_lineup_with_players_from_same_team(self):
        self.lineup_optimizer.reset_lineup()
        lineup = self.lineup_optimizer.optimize(teams={'LAL': 4, 'BOS': 4}).next()
        self.assertEqual(len(filter(lambda x: x.team == 'LAL', lineup.lineup)), 4)
        self.assertEqual(len(filter(lambda x: x.team == 'BOS', lineup.lineup)), 4)

    def test_lineup_with_players_from_same_positions(self):
        self.lineup_optimizer.reset_lineup()
        lineup = self.lineup_optimizer.optimize(positions={'C': 1}).next()
        self.assertEqual(len(filter(lambda x: x.positions[0] == 'C', lineup.lineup)), 2)

    def test_lineup_with_max_players(self):
        self.lineup_optimizer.reset_lineup()
        players = []
        players.append(Player('', 'P', 'P', ['PG'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['SG'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['SF'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['PF'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['C'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['PG'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['PF'], 'DEN', 10, 2))
        players.append(Player('', 'P', 'P', ['PG'], 'DEN', 10, 2))
        for player in players:
            self.lineup_optimizer.add_player_to_lineup(player)
        gen = self.lineup_optimizer.optimize()
        self.assertEqual(len(list(gen)), 1)

    def test_ratio(self):
        threshold = 0.8
        self.assertTrue(ratio('Blake Griffin', 'Blake Griffin') >= threshold)
        self.assertTrue(ratio('griffin', 'Blake Griffin') >= threshold)
        self.assertTrue(ratio('grifin', 'Blake Griffin') >= threshold)
        self.assertFalse(ratio('Hood', 'Blake Griffin') >= threshold)


def run_tests():
    unittest.main()


if __name__ == '__main__':
    run_tests()

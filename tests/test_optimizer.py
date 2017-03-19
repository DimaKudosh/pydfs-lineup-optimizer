from __future__ import absolute_import
import unittest
import json
from pydfs_lineup_optimizer import settings
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.settings import LineupPosition
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.utils import ratio


class TestLineupOptimizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open('tests/players.json', 'r') as file:
            players_dict = json.loads(file.read())['players']
            players = [Player(
                p['id'],
                p['first_name'],
                p['last_name'],
                p['positions'],
                p['team'],
                p['salary'],
                p['fppg']
            ) for p in players_dict]
        cls.players = players

    def setUp(self):
        self.lineup_optimizer = LineupOptimizer(settings.DraftKingsBasketballSettings)
        self.lineup_optimizer.load_players(self.players[:])

    def test_optimizer_positions_processing(self):
        positions = [
            LineupPosition('1', ('1', )),
            LineupPosition('2', ('2', )),
            LineupPosition('3', ('3', )),
            LineupPosition('23', ('2', '3')),
            LineupPosition('23', ('2', '3')),
            LineupPosition('all', ('1', '2', '3')),
            LineupPosition('all', ('1', '2', '3')),
        ]
        test_settings = type('TestSettings', (settings.BaseSettings, ), {})
        test_settings.positions = positions
        optimizer = LineupOptimizer(test_settings)
        self.assertEqual(len(optimizer._positions), 5)
        self.assertEqual(optimizer._positions[('1', )].min, 1)
        self.assertEqual(optimizer._positions[('1', )].max, 3)
        self.assertEqual(optimizer._positions[('2', )].min, 1)
        self.assertEqual(optimizer._positions[('2', )].max, 5)
        self.assertEqual(optimizer._positions[('3', )].min, 1)
        self.assertEqual(optimizer._positions[('3', )].max, 5)
        self.assertEqual(optimizer._positions[('2', '3')].min, 4)
        self.assertEqual(optimizer._positions[('2', '3')].max, 6)
        self.assertEqual(optimizer._positions[('1', '2', '3')].min, 7)
        self.assertEqual(optimizer._positions[('1', '2', '3')].max, 7)
        self.assertEqual(len(optimizer._not_linked_positions), 2)
        self.assertEqual(optimizer._not_linked_positions[('1', '2')].min, 2)
        self.assertEqual(optimizer._not_linked_positions[('1', '2')].max, 8)
        self.assertEqual(optimizer._not_linked_positions[('1', '3')].min, 2)
        self.assertEqual(optimizer._not_linked_positions[('1', '3')].max, 8)

    def test_add_player_to_lineup(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.add_player_to_lineup(self.players[0])
        self.assertTrue(self.players[0] in self.lineup_optimizer._lineup)

    def test_same_players_in_lineup(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.add_player_to_lineup(self.players[0])
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(self.players[0])

    def test_add_player_with_many_positions(self):
        players = [
            Player('', 'p1', 'p1', ['PG', 'SG'], 'DEN', 10, 200),
            Player('', 'p2', 'p2', ['PG'], 'DEN', 10, 200),
            Player('', 'p3', 'p3', ['PG'], 'DEN', 10, 200),
            Player('', 'p4', 'p4', ['PG'], 'DEN', 10, 200),
            Player('', 'p5', 'p5', ['PG', 'SG', 'SF'], 'DEN', 10, 200),
            Player('', 'p6', 'p6', ['SF'], 'DEN', 10, 200),
            Player('', 'p7', 'p7', ['SF'], 'DEN', 10, 190),
        ]
        self.lineup_optimizer._players.extend(players)
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
        players = [
            Player('', 'P', 'P', ['PG'], 'DEN', 10, 2),
            Player('', 'C', 'C', ['PG'], 'DEN', 10, 2),
            Player('', 'P', 'P', ['PG'], 'DEN', 10, 2),
        ]
        self.lineup_optimizer._players.extend(players)
        self.lineup_optimizer.add_player_to_lineup(players[0])
        self.lineup_optimizer.remove_player_from_lineup(players[0])
        self.assertEqual(len(self.lineup_optimizer._lineup), 0)
        self.lineup_optimizer.add_player_to_lineup(players[0])
        self.lineup_optimizer.add_player_to_lineup(players[1])
        self.lineup_optimizer.add_player_to_lineup(players[2])
        self.assertEqual(self.lineup_optimizer._positions[('PG',)].min, 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG',)].max, 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].min, 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].max, 1)
        self.lineup_optimizer.remove_player_from_lineup(players[0])
        self.assertEqual(self.lineup_optimizer._positions[('PG', )].min, 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG', )].max, 1)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].min, 1)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].max, 2)
        self.lineup_optimizer.remove_player_from_lineup(players[1])
        self.assertEqual(self.lineup_optimizer._positions[('PG', )].min, 0)
        self.assertEqual(self.lineup_optimizer._positions[('PG', )].max, 2)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].min, 2)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].max, 3)
        self.lineup_optimizer.remove_player_from_lineup(players[2])
        self.assertEqual(self.lineup_optimizer._positions[('PG', )].min, 1)
        self.assertEqual(self.lineup_optimizer._positions[('PG', )].max, 3)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].min, 3)
        self.assertEqual(self.lineup_optimizer._positions[('PG', 'SG')].max, 4)

    def test_lineup_with_players_from_same_team(self):
        self.lineup_optimizer.reset_lineup()
        lineup = next(self.lineup_optimizer.optimize(1, teams={'CAVS': 4, 'LAC': 4}))
        self.assertEqual(len(list(filter(lambda x: x.team == 'CAVS', lineup.lineup))), 4)
        self.assertEqual(len(list(filter(lambda x: x.team == 'LAC', lineup.lineup))), 4)

    def test_lineup_with_players_from_same_positions(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer._players.extend([
            Player('', 'p1', 'p1', ['C'], 'DEN', 10, 2),
            Player('', 'p2', 'p2', ['C'], 'DEN', 10, 2),
        ])
        lineup = next(self.lineup_optimizer.optimize(1, positions={'C': 1}))
        self.assertTrue(len(list(filter(lambda x: 'C' in x.positions, lineup.lineup))) >= 2)

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
        gen = self.lineup_optimizer.optimize(10)
        self.assertEqual(len(list(gen)), 1)

    def test_max_exposure(self):
        optimizer = self.lineup_optimizer
        players = [
            Player('', 'p1', 'p1', ['PG', 'SG'], 'DEN', 10, 200, max_exposure=0.3),
            Player('', 'p2', 'p2', ['PF', 'SF'], 'DEN', 10, 200),
            Player('', 'p3', 'p3', ['C'], 'DEN', 100, 2, max_exposure=0.35),
            Player('', 'p4', 'p4', ['PG'], 'DEN', 100, 2),
            Player('', 'p5', 'p5', ['PF'], 'DEN', 100, 2, max_exposure=0),
            Player('', 'p6', 'p6', ['SF'], 'DEN', 1, 2001, max_exposure=0),
        ]
        optimizer._players.extend(players)
        optimizer.add_player_to_lineup(players[2])
        optimizer.add_player_to_lineup(players[3])
        optimizer.add_player_to_lineup(players[4])
        lineups_with_players = [0 for _ in players]
        for lineup in optimizer.optimize(10, max_exposure=0.5):
            for i, player in enumerate(players):
                if player in lineup.players:
                    lineups_with_players[i] += 1
        self.assertEqual(lineups_with_players[0], 3)
        self.assertEqual(lineups_with_players[1], 5)
        self.assertEqual(lineups_with_players[2], 4)
        self.assertEqual(lineups_with_players[3], 5)
        self.assertEqual(lineups_with_players[4], 0)
        self.assertEqual(lineups_with_players[5], 0)
        self.assertEqual(optimizer.lineup, players[2:5])

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

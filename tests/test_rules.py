from __future__ import absolute_import, division
import unittest
import mock
from copy import deepcopy
from collections import Counter
from pydfs_lineup_optimizer import get_optimizer
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.rules import ProjectedOwnershipRule
from utils import create_players, load_players


class OptimizerRulesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.players = load_players()

    def setUp(self):
        self.lineup_optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        self.lineup_optimizer.load_players(self.players[:])

    def test_min_salary_cap(self):
        player = Player(1, 'p1', 'p1', ['PG'], 'team1', 1, 200)
        self.lineup_optimizer.extend_players([player])
        lineup = next(self.lineup_optimizer.optimize(1))
        min_salary_cap = 50000
        self.assertTrue(lineup.salary_costs < min_salary_cap)
        self.lineup_optimizer.set_min_salary_cap(min_salary_cap)
        lineup = next(self.lineup_optimizer.optimize(1))
        self.assertEqual(lineup.salary_costs, min_salary_cap)
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.add_player_to_lineup(player)
            next(self.lineup_optimizer.optimize(1))
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.set_min_salary_cap(min_salary_cap * 2)

    def test_with_injured_optimize(self):
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        cool_player = Player(1, 'P1', 'P1', ['PG'], 'team1', 1, 200)
        optimizer.load_players(self.players)
        optimizer.extend_players([cool_player])
        lineup = next(optimizer.optimize(1))
        self.assertIn(cool_player, lineup)
        cool_player.is_injured = True
        lineup = next(optimizer.optimize(1))
        self.assertNotIn(cool_player, lineup)
        lineup = next(optimizer.optimize(1, with_injured=True))
        self.assertIn(cool_player, lineup)

    def test_not_repeating_players(self):
        total_lineups = 5
        custom_players = create_players(['PG', 'SG', 'SF', 'PF', 'C', 'PG', 'SF'])
        for player in custom_players:
            player.fppg = 1000
        self.lineup_optimizer.extend_players(custom_players)
        custom_players_in_lineup = []
        for lineup in self.lineup_optimizer.optimize(total_lineups):
            custom_players_in_lineup.append(sum(1 for player in lineup.players if player in custom_players))
        self.assertListEqual(custom_players_in_lineup, [7] * total_lineups)
        self.lineup_optimizer.set_max_repeating_players(3)
        custom_players_in_lineup = []
        for lineup in self.lineup_optimizer.optimize(total_lineups):
            custom_players_in_lineup.append(sum(1 for player in lineup.players if player in custom_players))
        self.assertListEqual(custom_players_in_lineup, [7] + [3] * (total_lineups - 1))
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.set_max_repeating_players(8)
        with self.assertRaises(LineupOptimizerException):
            self.lineup_optimizer.set_max_repeating_players(0)

    def test_unique_player_rule(self):
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.GOLF)
        players = create_players(['G'] * 10)
        high_fppg_player = Player(1, 'High FPPG', 'Player', ['G'], '', 50, 200)
        players.extend([high_fppg_player] * 2)
        optimizer.load_players(players)
        lineup = next(optimizer.optimize(1))
        self.assertEqual(len([p for p in lineup if p == high_fppg_player]), 1)

    def test_positions_from_same_team(self):
        optimizer = get_optimizer(Site.YAHOO, Sport.BASKETBALL)
        players = [
            Player(1, 'p1', 'p1', ['PG'], 'team1', 10, 200),
            Player(2, 'p2', 'p2', ['SG'], 'team2', 10, 200),
            Player(3, 'p3', 'p3', ['SF'], 'team3', 10, 200),
            Player(4, 'p4', 'p4', ['PF'], 'team4', 10, 200),
            Player(5, 'p5', 'p5', ['C'], 'team5', 10, 200),
            Player(6, 'p6', 'p6', ['PG', 'SG'], 'team6', 10, 200),
            Player(7, 'p7', 'p7', ['SF', 'PF'], 'team7', 10, 200),
            Player(8, 'p8', 'p8', ['PG', 'SG', 'SF'], 'team8', 10, 200),
            Player(9, 'p9', 'p9', ['C'], 'team1', 10, 5),
            Player(10, 'p10', 'p10', ['SF'], 'team1', 10, 2),
            Player(11, 'p11', 'p11', ['PF', 'C'], 'team1', 10, 2),
        ]
        optimizer.load_players(players)
        lineup = next(optimizer.optimize(1))
        self.assertEqual(len(set([p.team for p in lineup.lineup])), 8)
        optimizer.set_positions_for_same_team(['PG', 'C'])
        lineup = next(optimizer.optimize(1))
        self.assertEqual(len(set([p.team for p in lineup.lineup])), 7)
        self.assertTrue(all(players[i] in lineup.lineup for i in [0, 8]))
        optimizer.set_positions_for_same_team(['PG', 'SF', 'C'])
        lineup = next(optimizer.optimize(1))
        self.assertEqual(len(set([p.team for p in lineup.lineup])), 6)
        self.assertTrue(all(players[i] in lineup.lineup for i in [0, 8, 9]))
        optimizer.set_positions_for_same_team(['PG', 'SF', 'C', 'C'])
        lineup = next(optimizer.optimize(1))
        self.assertEqual(len(set([p.team for p in lineup.lineup])), 5)
        self.assertTrue(all(players[i] in lineup.lineup for i in [0, 8, 9, 10]))
        # Test reset
        optimizer.set_positions_for_same_team(None)
        lineup = next(optimizer.optimize(1))
        self.assertEqual(len(set([p.team for p in lineup.lineup])), 8)

    def test_max_from_one_team(self):
        max_from_one_team = 1
        optimizer = self.lineup_optimizer
        players = [
            Player(1, 'p1', 'p1', ['PG', 'SG'], 'DEN', 10, 200),
            Player(2, 'p2', 'p2', ['PF', 'SF'], 'DEN', 10, 200),
            Player(3, 'p3', 'p3', ['C'], 'DEN', 10, 200),
        ]
        optimizer.extend_players(players)
        with mock.patch('pydfs_lineup_optimizer.LineupOptimizer.max_from_one_team', new_callable=mock.PropertyMock) \
                as mock_max_from_one_team:
            mock_max_from_one_team.return_value = max_from_one_team
            lineup = next(optimizer.optimize(1))
            team_counter = Counter([p.team for p in lineup.lineup])
            self.assertTrue(all([team_players <= max_from_one_team for team_players in team_counter.values()]))
            with self.assertRaises(LineupOptimizerException):
                self.lineup_optimizer.set_players_from_one_team({'DEN': 3})
                next(optimizer.optimize(1))
            optimizer.add_player_to_lineup(players[0])
            with self.assertRaises(LineupOptimizerException):
                optimizer.add_player_to_lineup(players[1])

    def test_randomness(self):
        optimized_lineup = next(self.lineup_optimizer.optimize(1))
        random_lineup = next(self.lineup_optimizer.optimize(1, randomness=True))
        self.assertTrue(optimized_lineup.fantasy_points_projection >= random_lineup.fantasy_points_projection)
        self.assertTrue(
            random_lineup.fantasy_points_projection >
            (1 - self.lineup_optimizer._max_deviation) * optimized_lineup.fantasy_points_projection
        )

    def test_lineup_with_players_from_same_positions(self):
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        optimizer.load_players(create_players(['PG', 'SG', 'SF', 'PF', 'C', 'PG', 'SF', 'PF']))
        optimizer.extend_players([
            Player(1, 'p1', 'p1', ['C'], 'DEN', 1000, 2),
            Player(2, 'p2', 'p2', ['C'], 'DEN', 1000, 2),
        ])
        optimizer.set_players_with_same_position({'C': 1})
        lineup = next(optimizer.optimize(1))
        self.assertTrue(len(list(filter(lambda x: 'C' in x.positions, lineup.lineup))) >= 2)

    def test_lineup_with_players_from_same_team(self):
        self.lineup_optimizer.reset_lineup()
        self.lineup_optimizer.set_players_from_one_team({'CAVS': 4, 'LAC': 4})
        lineup = next(self.lineup_optimizer.optimize(1))
        self.assertEqual(len(list(filter(lambda x: x.team == 'CAVS', lineup.lineup))), 4)
        self.assertEqual(len(list(filter(lambda x: x.team == 'LAC', lineup.lineup))), 4)

    def test_max_exposure(self):
        optimizer = self.lineup_optimizer
        players = [
            Player(1, 'p1', 'p1', ['PG', 'SG'], 'DEN', 10, 200, max_exposure=0.3),
            Player(2, 'p2', 'p2', ['PF', 'SF'], 'DEN', 10, 200),
            Player(3, 'p3', 'p3', ['C'], 'DEN', 100, 2, max_exposure=0.35),
            Player(4, 'p4', 'p4', ['PG'], 'DEN', 100, 2),
            Player(5, 'p5', 'p5', ['PF'], 'DEN', 100, 2, max_exposure=0),
            Player(6, 'p6', 'p6', ['SF'], 'DEN', 1, 2001, max_exposure=0),
        ]
        optimizer.extend_players(players)
        optimizer.add_player_to_lineup(players[2])
        optimizer.add_player_to_lineup(players[3])
        with self.assertRaises(LineupOptimizerException):
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
        self.assertEqual(optimizer.locked_players, players[2:4])

    def test_min_exposure(self):
        optimizer = self.lineup_optimizer
        players = [
            Player(1, 'p1', 'p1', ['PG', 'SG'], 'DEN', 1000, 0, min_exposure=0.3),
            Player(2, 'p2', 'p2', ['C'], 'DEN', 1000, 0, min_exposure=0.35),
            Player(3, 'p3', 'p3', ['C'], 'DEN', 1000, 0, min_exposure=1),
        ]
        optimizer.extend_players(players)
        lineups_with_players = [0 for _ in players]
        for lineup in optimizer.optimize(10):
            for i, player in enumerate(players):
                if player in lineup.players:
                    lineups_with_players[i] += 1
        self.assertEqual(lineups_with_players[0], 3)
        self.assertEqual(lineups_with_players[1], 4)
        self.assertEqual(lineups_with_players[2], 10)


class ProjectedOwnershipTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.players = [
            Player(1, 'Golf Player 1', '', ['G'], '', 5000, 200, projected_ownership=0.95),
            Player(2, 'Golf Player 2', '', ['G'], '', 5000, 20, projected_ownership=0.7),
            Player(3, 'Golf Player 3', '', ['G'], '', 5000, 20, projected_ownership=0.7),
            Player(4, 'Golf Player 4', '', ['G'], '', 5000, 20, projected_ownership=0.7),
            Player(5, 'Golf Player 5', '', ['G'], '', 5000, 5, projected_ownership=0.5),
            Player(6, 'Golf Player 6', '', ['G'], '', 5000, 5, projected_ownership=0.5),
            Player(7, 'Golf Player 7', '', ['G'], '', 5000, 5, projected_ownership=0.5),
            Player(8, 'Golf Player 8', '', ['G'], '', 5000, 5, projected_ownership=0.5),
            Player(9, 'Golf Player 9', '', ['G'], '', 5000, 5, projected_ownership=0.5),
            Player(10, 'Golf Player 10', '', ['G'], '', 5000, 5, projected_ownership=0.5),
        ]

    def setUp(self):
        self.optimizer = get_optimizer(Site.DRAFTKINGS, Sport.GOLF)
        self.optimizer.load_players(self.players)

    def test_min_projection_greater_than_max(self):
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.set_projected_ownership(1, 0.5)

    def test_clear_projected_ownership_rule(self):
        self.optimizer.set_projected_ownership(0.5, 1)
        self.optimizer.set_projected_ownership()  # Should remove rule
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.remove_rule(ProjectedOwnershipRule, silent=False)

    def test_min_projected_ownership_constraint(self):
        min_projected_ownership = 0.6
        self.optimizer.set_projected_ownership(min_projected_ownership=min_projected_ownership)
        lineup = next(self.optimizer.optimize(n=1))
        self.assertGreaterEqual(sum([p.projected_ownership for p in lineup.players]) / len(lineup.players),
                                min_projected_ownership)

    def test_max_projected_ownership_constraint(self):
        max_projected_ownership = 0.6
        self.optimizer.set_projected_ownership(max_projected_ownership=max_projected_ownership)
        lineup = next(self.optimizer.optimize(n=1))
        self.assertLessEqual(sum([p.projected_ownership for p in lineup.players]) / len(lineup.players),
                             max_projected_ownership)

    def test_both_projected_ownership_constraint(self):
        min_projected_ownership = 0.49
        max_projected_ownership = 0.51
        self.optimizer.set_projected_ownership(min_projected_ownership, max_projected_ownership)
        lineup = next(self.optimizer.optimize(n=1))
        self.assertTrue(all([p.projected_ownership == 0.5 for p in lineup.players]))

    def test_projected_ownership_for_locked_players(self):
        max_projected_ownership = 0.59  # ownership for generating best player and 5 worst players
        self.optimizer.add_player_to_lineup(self.players[1])
        self.optimizer.set_projected_ownership(max_projected_ownership=max_projected_ownership)
        lineup = next(self.optimizer.optimize(n=1))
        self.assertTrue(self.players[0] not in lineup.players)

    def test_projected_ownership_constraint_for_user_without_ownership(self):
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.GOLF)
        players = deepcopy(self.players)
        for player in players[1:]:
            player.projected_ownership = None
        optimizer.load_players(players)
        optimizer.set_projected_ownership(max_projected_ownership=0.9)
        lineup = next(optimizer.optimize(n=1))
        self.assertTrue(self.players[0] not in lineup.players)

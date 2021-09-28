from __future__ import absolute_import, division
import unittest
from collections import Counter, defaultdict
from parameterized import parameterized
from pydfs_lineup_optimizer import get_optimizer
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.player import Player, GameInfo
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.utils import list_intersection
from pydfs_lineup_optimizer.stacks import GameStack, TeamStack, PositionsStack
from tests.utils import load_players


class StacksRuleTestCase(unittest.TestCase):
    def setUp(self):
        self.players = load_players()
        self.optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        self.optimizer.settings.max_from_one_team = 4
        self.test_team = 'TEST'
        self.spacing_players = [
            Player('1', '1', '1', ['PG'], self.test_team, 100, 4, roster_order=1),
            Player('2', '2', '2', ['SG'], self.test_team, 100, 3, roster_order=2),
            Player('3', '3', '3', ['SG'], self.test_team, 100, 3, roster_order=2),
            Player('4', '4', '4', ['SF'], self.test_team, 100, 5, roster_order=3),
            Player('5', '5', '5', ['PF'], self.test_team, 100, 1, roster_order=4),
        ]
        self.optimizer.player_pool.load_players(self.players + self.spacing_players)

    def test_stacks_correctness(self):
        stacks = [4, 2]
        for stack in stacks:
            self.optimizer.add_stack(TeamStack(stack))
        lineup = next(self.optimizer.optimize(n=1))
        teams = Counter([player.team for player in lineup])
        self.assertListEqual(stacks, [stack[1] for stack in Counter(teams).most_common(len(stacks))])

    def test_stack_greater_than_max_from_one_team(self):
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.add_stack(TeamStack(5))

    def test_stacks_for_positions(self):
        position = 'PG'
        self.optimizer.add_stack(TeamStack(4, for_positions=[position]))
        lineup = next(self.optimizer.optimize(n=1))
        all_position_players_teams = [player.team for player in lineup if position in player.positions]
        self.assertEqual(len(set(all_position_players_teams)), 1)

    @parameterized.expand([
        (3, [1, 3]),
        (2, [2, 3]),
        (1, [2, 2]),
    ])
    def test_stacks_with_spacing(self, spacing, expected):
        self.optimizer.add_stack(TeamStack(2, spacing=spacing))
        lineup = next(self.optimizer.optimize(n=1))
        spacings = [player.roster_order for player in lineup if player in self.spacing_players]
        spacings.sort()
        self.assertEqual(spacings, expected)


class TestPositionsFromSameTeamTestCase(unittest.TestCase):
    def setUp(self):
        self.optimizer = get_optimizer(Site.YAHOO, Sport.BASKETBALL)
        self.first_team = 'TEST'
        self.second_team = 'TEST2'
        self.players = [
            Player('1', 'p1', 'p1', ['PG'], self.first_team, 10, 200),
            Player('2', 'p2', 'p2', ['SG'], 'team2', 10, 200),
            Player('3', 'p3', 'p3', ['SF'], 'team3', 10, 200),
            Player('4', 'p4', 'p4', ['PF'], 'team4', 10, 200),
            Player('5', 'p5', 'p5', ['C'], 'team5', 10, 200),
            Player('6', 'p6', 'p6', ['PG', 'SG'], 'team6', 10, 200),
            Player('7', 'p7', 'p7', ['SF', 'PF'], 'team7', 10, 200),
            Player('8', 'p8', 'p8', ['SF', 'PF'], self.second_team, 10, 2),
            Player('9', 'p9', 'p9', ['PG', 'SG', 'SF'], self.second_team, 10, 2),
            Player('10', 'p10', 'p10', ['C'], self.first_team, 10, 2),
            Player('11', 'p11', 'p11', ['SF'], self.first_team, 10, 2),
            Player('12', 'p12', 'p12', ['PF', 'C'], self.first_team, 10, 2),
        ]
        self.optimizer.player_pool.load_players(self.players)

    @parameterized.expand([
        (['PG', 'C'], ),
        (['PG', 'SF', 'C'], ),
        (['PG', 'SF', 'C', 'C'], ),
    ])
    def test_positions_from_same_team(self, combination):
        self.optimizer.stacks = []
        self.optimizer.add_stack(PositionsStack(combination))
        lineup = next(self.optimizer.optimize(1))
        self.assertEqual(len([p for p in lineup.lineup if p.team == self.first_team]), len(combination))

    def test_multiple_positions_from_same_team(self):
        from_same_team = (['PG', 'C'], ['SG', 'SF'])
        for position_stack in from_same_team:
            self.optimizer.add_stack(PositionsStack(position_stack))
        lineup = next(self.optimizer.optimize(1))
        self.assertEqual(len([p for p in lineup.lineup if p.team == self.first_team]), len(from_same_team[0]))
        self.assertEqual(len([p for p in lineup.lineup if p.team == self.second_team]), len(from_same_team[1]))

    def test_positions_stack_greater_than_max_from_one_team(self):
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.add_stack(PositionsStack(['PG', 'PG', 'SG', 'SG', 'SF', 'PF', 'C']))

    def test_incorrect_position_names(self):
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.add_stack(PositionsStack(['G']))

    def test_empty_positions_stacks_tuple(self):
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.add_stack(PositionsStack([]))

    def test_positions_from_same_team_with_combo_position(self):
        self.optimizer.add_stack(PositionsStack(['PG', ('SF', 'C')]))
        lineups = list(self.optimizer.optimize(2))
        stack = ('PG', 'SF', 'C')
        players_in_stack = max([
            len([p for p in lineup if p.team == self.first_team and list_intersection(p.positions, stack)])
            for lineup in lineups
        ])
        self.assertEqual(players_in_stack, 2)


class GameStackRuleTestCase(unittest.TestCase):
    def setUp(self):
        self.players = load_players()
        self.optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        self.optimizer.settings.max_from_one_team = 4
        self.home_team = 'Home'
        self.away_team = 'Away'
        self.game_info = GameInfo(
            home_team=self.home_team,
            away_team=self.away_team,
            starts_at=None,
        )
        self.game_players = [
            Player('1', '1', '1', ['PG'], self.home_team, 1000, 3, game_info=self.game_info),
            Player('2', '2', '2', ['SG'], self.home_team, 1000, 3, game_info=self.game_info),
            Player('3', '3', '3', ['C'], self.home_team, 1000, 3, game_info=self.game_info),
            Player('4', '4', '4', ['SG'], self.away_team, 1000, 1, game_info=self.game_info),
            Player('5', '5', '5', ['SF'], self.away_team, 1000, 1, game_info=self.game_info),
            Player('6', '6', '6', ['PF'], self.away_team, 1000, 1, game_info=self.game_info),
        ]
        self.optimizer.player_pool.load_players(self.players + self.game_players)

    @parameterized.expand([(i, ) for i in (range(2, 7))])
    def test_stacks_correctness(self, size):
        self.optimizer.add_stack(GameStack(size))
        lineup = next(self.optimizer.optimize(n=1))
        players_from_game = len([player for player in self.game_players if player in lineup])
        self.assertEqual(players_from_game, size)

    def test_stacks_correctness_min_from_team(self):
        self.optimizer.add_stack(GameStack(4, min_from_team=2))
        lineup = next(self.optimizer.optimize(n=1))
        players_by_team = defaultdict(int)
        for player in lineup:
            players_by_team[player.team] += 1
        self.assertEqual(players_by_team[self.home_team], 2)
        self.assertEqual(players_by_team[self.away_team], 2)

    def test_stacks_incorrect_params(self):
        with self.assertRaises(LineupOptimizerException):
            self.optimizer.add_stack(GameStack(4, min_from_team=3))

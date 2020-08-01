from __future__ import absolute_import, division
import unittest
from datetime import datetime, timedelta
from pytz import timezone
from unittest.mock import patch, PropertyMock
from pydfs_lineup_optimizer import get_optimizer
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.player import LineupPlayer, GameInfo
from .utils import create_players


class LateSwapTestCase(unittest.TestCase):
    def setUp(self):
        self.future_game_info = GameInfo(home_team='H', away_team='A', game_started=False,
                                         starts_at=datetime.now(timezone('EST')) + timedelta(days=1))
        self.finished_game_info = GameInfo(home_team='H2', away_team='A2', game_started=False,
                                           starts_at=datetime.now(timezone('EST')) - timedelta(days=1))
        self.lineup_optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
        self.lineup_optimizer.settings.min_games = None
        positions = ['PG', 'SG', 'SF', 'PF', 'C', 'PG/SG', 'SF/PF', 'C']
        self.active_players = create_players(positions, game_info=self.future_game_info, salary=5000, fppg=20)
        self.inactive_players = create_players(positions, game_info=self.finished_game_info, salary=4500, fppg=10)
        self.lineup_optimizer.load_players(self.active_players + self.inactive_players)
        self.lineup = Lineup([
            LineupPlayer(self.active_players[0], 'PG'),
            LineupPlayer(self.inactive_players[1], 'SG'),
            LineupPlayer(self.active_players[2], 'SF'),
            LineupPlayer(self.inactive_players[3], 'PF'),
            LineupPlayer(self.active_players[4], 'C'),
            LineupPlayer(self.inactive_players[5], 'G'),
            LineupPlayer(self.active_players[6], 'F'),
            LineupPlayer(self.inactive_players[7], 'UTIL'),
        ])

    def test_late_swap_optimize(self):
        players_in_action = {player: player.lineup_position for player in self.lineup if player.is_game_started}
        lineup = next(self.lineup_optimizer.optimize_lineups([self.lineup]))
        for player in lineup:
            if not player.is_game_started:
                continue
            self.assertIn(player, players_in_action)
            position = players_in_action[player]
            self.assertEqual(position, player.lineup_position)

    def test_late_swap_optimize_with_all_inactive_players(self):
        with patch('pydfs_lineup_optimizer.player.Player.is_game_started', new_callable=PropertyMock) as \
                mock_is_game_started:
            mock_is_game_started.return_value = False
            lineup = next(self.lineup_optimizer.optimize_lineups([self.lineup]))
            for player in lineup:
                self.assertNotIn(player, self.inactive_players)

    def test_late_swap_optimize_with_all_active_players(self):
        with patch('pydfs_lineup_optimizer.player.Player.is_game_started', new_callable=PropertyMock) as \
                mock_is_game_started:
            mock_is_game_started.return_value = True
            lineup = next(self.lineup_optimizer.optimize_lineups([self.lineup]))
            for player, new_lineup_player in zip(self.lineup, lineup):
                self.assertEqual(player, new_lineup_player)

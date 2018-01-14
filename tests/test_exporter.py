from __future__ import absolute_import
import sys
import unittest
from mock import mock_open, patch
from pydfs_lineup_optimizer import Site, Sport, get_optimizer, CSVLineupExporter, Player


if sys.version_info < (3, ):
    OPEN_METHOD = '__builtin__.open'
else:
    OPEN_METHOD = 'builtins.open'


class TestLineupExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        optimizer = get_optimizer(Site.YAHOO, Sport.BASKETBALL)
        cls.players = [
            Player(1, 'First Name 1', 'Last Name 1', ['PG'], 'Team1', 20, 20),
            Player(2, 'First Name 2', 'Last Name 2', ['SG'], 'Team2', 20, 20),
            Player(3, 'First Name 3', 'Last Name 3', ['SF'], 'Team3', 20, 20),
            Player(4, 'First Name 4', 'Last Name 4', ['PF'], 'Team4', 20, 20),
            Player(5, 'First Name 5', 'Last Name 5', ['C'], 'Team5', 20, 20),
            Player(6, 'First Name 6', 'Last Name 6', ['PG', 'SG'], 'Team6', 20, 20),
            Player(7, 'First Name 7', 'Last Name 7', ['SF', 'PF'], 'Team7', 20, 20),
            Player(8, 'First Name 8', 'Last Name 8', ['PG', 'SG', 'SF'], 'Team8', 20, 20),
        ]
        optimizer.load_players(cls.players)
        cls.lineups = list(optimizer.optimize(1))

    @patch(OPEN_METHOD, new_callable=mock_open)
    def test_csv_exporter(self, mocked_open):
        filename = 'test.csv'
        CSVLineupExporter(self.lineups).export(filename)
        mocked_open.assert_called_once_with(filename, 'w')
        lineup = self.lineups[0]
        header = ','.join(['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL', 'Budget', 'FPPG']) + '\r\n'
        body = [CSVLineupExporter.render_player(player) for player in lineup.lineup]
        body.extend((str(lineup.salary_costs), str(lineup.fantasy_points_projection)))
        body = ','.join(body) + '\r\n'
        mocked_open.return_value.write.assert_any_call(header)
        mocked_open.return_value.write.assert_any_call(body)

    @patch(OPEN_METHOD, new_callable=mock_open)
    def test_csv_exporter_with_custom_player_render(self, mocked_open):
        filename = 'test.csv'
        player_render = lambda player: '%s %s' % (player.full_name, player.team)
        CSVLineupExporter(self.lineups).export(filename, player_render)
        mocked_open.assert_called_once_with(filename, 'w')
        lineup = self.lineups[0]
        header = ','.join(['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL', 'Budget', 'FPPG']) + '\r\n'
        body = [player_render(player) for player in lineup.lineup]
        body.extend((str(lineup.salary_costs), str(lineup.fantasy_points_projection)))
        body = ','.join(body) + '\r\n'
        mocked_open.return_value.write.assert_any_call(header)
        mocked_open.return_value.write.assert_any_call(body)

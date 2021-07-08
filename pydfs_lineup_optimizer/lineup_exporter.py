import csv
from typing import Iterable, Callable, Dict, List, Tuple, TYPE_CHECKING


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.lineup import Lineup
    from pydfs_lineup_optimizer.player import LineupPlayer


class LineupExporter:
    def __init__(self, lineups: Iterable['Lineup']):
        self.lineups = lineups

    @staticmethod
    def render_player(player: 'LineupPlayer') -> str:
        result = player.full_name  # type: str
        if player.id:
            result += '(%s)' % player.id
        return result

    def export(self, filename: str, render_func: Callable[['LineupPlayer'], str] = None):
        raise NotImplementedError


class CSVLineupExporter(LineupExporter):
    EXTRA_COLUMNS = ('Budget', 'FPPG')  # type: Tuple[str, ...]
    COLUMNS_MAPPING = {}  # type: Dict[str , str]

    def _get_extra_columns(self, lineup: 'Lineup') -> List[str]:
        return [
            str(lineup.salary_costs),
            str(lineup.fantasy_points_projection),
        ]

    def export(self, filename, render_func=None):
        with open(filename, 'w', newline='') as csvfile:
            lineup_writer = csv.writer(csvfile, delimiter=',')
            for index, lineup in enumerate(self.lineups):
                if index == 0:
                    header = [self.COLUMNS_MAPPING.get(player.lineup_position, player.lineup_position)
                              for player in lineup.lineup]
                    header.extend(self.EXTRA_COLUMNS)
                    lineup_writer.writerow(header)
                row = [(render_func or self.render_player)(player) for player in lineup.lineup]
                row.extend(self._get_extra_columns(lineup))
                lineup_writer.writerow(row)


class FantasyDraftCSVLineupExporter(LineupExporter):
    def export(self, filename, render_func=None):
        if not self.lineups:
            return
        total_players = 0
        with open(filename, 'r') as csvfile:
            lines = list(csv.reader(csvfile))
            for i, lineup in enumerate(self.lineups, start=1):
                if i >= len(lines):
                    lines.append([])
                players_list = [(render_func or self.render_player)(player) for player in lineup.lineup]
                if not total_players:
                    total_players = len(players_list)
                lines[i] = players_list + lines[i][total_players:]
            for line_order in range(i, len(lines) - 1):
                lines[line_order] = [''] * total_players + lines[line_order][total_players:]
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(lines)


class YahooCSVLineupExporter(CSVLineupExporter):
    @staticmethod
    def render_player(player: 'LineupPlayer') -> str:
        return str(player.id)


class FanDuelCSVLineupExporter(CSVLineupExporter):
    EXTRA_COLUMNS = ()
    COLUMNS_MAPPING = {
        'MVP': 'MVP - 2X Points',
        'STAR': 'STAR - 1.5X Points',
        'PRO': 'PRO - 1.2X Points',
        'CAPTAIN': 'Captain - 1.5x Pts',
    }

    def _get_extra_columns(self, lineup):
        return []

    @staticmethod
    def render_player(player: 'LineupPlayer') -> str:
        return str(player.id)

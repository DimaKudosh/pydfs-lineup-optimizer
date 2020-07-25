import csv
from copy import deepcopy
from itertools import islice
from typing import List, Dict
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player, GameInfo


class FanDuelCSVImporter(CSVImporter):  # pragma: nocover
    def _row_to_player(self, row: Dict) -> Player:
        game_info = None
        try:
            away_team, home_team = row.get('Game', '').split('@')
            game_info = GameInfo(home_team, away_team, None, False)
        except ValueError:
            pass
        try:
            player = Player(
                row['Id'],
                row['First Name'],
                row['Last Name'],
                row['Position'].split('/'),
                row['Team'],
                float(row['Salary']),
                float(row['FPPG']),
                is_injured=True if row['Injury Indicator'].strip() else False,
                game_info=game_info,
                **self.get_player_extra(row)
            )
        except KeyError:
            raise LineupOptimizerIncorrectCSV
        return player

    def import_players(self) -> List[Player]:
        with open(self.filename, 'r') as csv_file:
            start_line = 0  # Find line with 'FPPG', that's where players data starts
            while True:
                line = csv_file.readline()
                if 'FPPG' in line:
                    csv_file.seek(0)
                    csv_data = csv.DictReader(islice(csv_file, start_line, None),
                                              skipinitialspace=True)
                    return [self._row_to_player(row) for row in csv_data]
                elif line == '':
                    raise LineupOptimizerIncorrectCSV
                else:
                    start_line += 1


class FanDuelMVPCSVImporter(FanDuelCSVImporter):
    def import_players(self):
        players = super().import_players()
        mvps = []
        for player in players:
            mvp_player = deepcopy(player)
            mvp_player.fppg *= 1.5
            mvp_player._original_positions = player.positions
            mvp_player.positions = ['MVP']
            mvps.append(mvp_player)
        players.extend(mvps)
        return players


class FanDuelLOLCSVImporter(FanDuelCSVImporter):
    def import_players(self):
        players = super().import_players()
        stars = []
        for player in players:
            if 'TEAM' in player.positions:
                continue
            star_player = deepcopy(player)
            star_player.fppg *= 1.5
            star_player._original_positions = player.positions
            star_player.positions = ['STAR']
            stars.append(star_player)
        players.extend(stars)
        return players

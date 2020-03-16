import csv
from itertools import islice
from typing import List, Dict
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player, GameInfo
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site


@SitesRegistry.register_csv_importer
class FANDUELCSVImporter(CSVImporter):  # pragma: nocover
    site = Site.FANDUEL

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
                True if row['Injury Indicator'].strip() else False,
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

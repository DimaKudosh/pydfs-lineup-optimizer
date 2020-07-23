import csv
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player, GameInfo


class YahooCSVImporter(CSVImporter):  # pragma: nocover
    @staticmethod
    def _process_cell(val: str) -> str:
        return val.strip()

    def import_players(self):
        players = []
        with open(self.filename, 'r') as csvfile:
            csv_data = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csv_data:
                player_id = self._process_cell(row['ID'])
                if not player_id:
                    continue
                game_info = None
                try:
                    away_team, home_team = self._process_cell(row.get('Game', '')).split('@')
                    game_info = GameInfo(home_team, away_team, None, False)
                except ValueError:
                    pass
                try:
                    player = Player(
                        player_id,
                        self._process_cell(row['First Name']),
                        self._process_cell(row['Last Name']),
                        self._process_cell(row['Position']).split('/'),
                        self._process_cell(row['Team']),
                        float(self._process_cell(row['Salary'])),
                        float(self._process_cell(row['FPPG'])),
                        is_injured=True if self._process_cell(row['Injury Status']) else False,
                        game_info=game_info,
                        **self.get_player_extra(row)
                    )
                except KeyError:
                    raise LineupOptimizerIncorrectCSV
                players.append(player)
        return players

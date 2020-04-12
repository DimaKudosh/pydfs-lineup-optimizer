import csv
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player, GameInfo


class YahooCSVImporter(CSVImporter):  # pragma: nocover
    def import_players(self):
        players = []
        with open(self.filename, 'r') as csvfile:
            csv_data = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csv_data:
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
                        is_injured=True if row['Injury Status'].strip() else False,
                        game_info=game_info,
                        **self.get_player_extra(row)
                    )
                except KeyError:
                    raise LineupOptimizerIncorrectCSV
                players.append(player)
        return players

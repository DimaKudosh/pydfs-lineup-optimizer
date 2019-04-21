import csv
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player, GameInfo
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site


@SitesRegistry.register_csv_importer
class FanDuelCSVImporter(CSVImporter):  # pragma: nocover
    site = Site.FANDUEL

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
                    max_exposure = row.get('Max Exposure')
                    player = Player(
                        row['Id'],
                        row['First Name'],
                        row['Last Name'],
                        row['Position'].split('/'),
                        row['Team'],
                        float(row['Salary']),
                        float(row['FPPG']),
                        True if row['Injury Indicator'].strip() else False,
                        max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None,
                        game_info=game_info,
                    )
                except KeyError:
                    raise LineupOptimizerIncorrectCSV
                players.append(player)
        return players

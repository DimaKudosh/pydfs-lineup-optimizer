import csv
from itertools import islice
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site


@SitesRegistry.register_csv_importer
class DraftKingsCSVImporter(CSVImporter):
    site = Site.DRAFTKINGS

    def _row_to_player(self, row):
        try:
            max_exposure = row.get('Max Exposure', '').replace('%', '')
            name = row['Name'].split()
            player = Player(
                row['ID'],
                name[0],
                name[1] if len(name) > 1 else '',
                row['Position'].split('/'),
                row['TeamAbbrev'],
                float(row['Salary']),
                float(row['AvgPointsPerGame']),
                max_exposure=float(max_exposure) if max_exposure else None
            )
        except KeyError:
            raise LineupOptimizerIncorrectCSV
        return player

    def import_players(self):  # pragma: no cover
        with open(self.filename, 'r') as csvfile:
            first_line = csvfile.readline()
            csvfile.seek(0)
            if 'TeamAbbrev' in first_line:
                csv_data = csv.DictReader(csvfile, skipinitialspace=True)
            else:
                csv_data = csv.DictReader(islice(csvfile, 7, None),
                                          skipinitialspace=True)
            players = [self._row_to_player(row) for row in csv_data]
        return players

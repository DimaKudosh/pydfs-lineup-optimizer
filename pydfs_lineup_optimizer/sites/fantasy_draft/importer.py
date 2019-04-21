import csv
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site


@SitesRegistry.register_csv_importer
class FantasyDraftCSVImporter(CSVImporter):  # pragma: nocover
    site = Site.FANTASY_DRAFT

    def import_players(self):
        players = []
        with open(self.filename, 'r') as csvfile:
            csv_data = csv.DictReader(csvfile, skipinitialspace=True)
            for i, row in enumerate(csv_data):
                try:
                    name = row['Name'].split()
                    max_exposure = row.get('Max Exposure')
                    fppg = row.get('Avg FPPG') or row.get('Avg FPPT')
                    if not fppg:
                        raise LineupOptimizerIncorrectCSV
                    player = Player(
                        str(i),
                        name[0],
                        name[1] if len(name) > 1 else '',
                        row['Position'].split('/'),
                        row.get('Team', row.get('Game', '')),
                        float(row['Salary'].replace('$', '').replace(',', '')),
                        float(fppg),
                        max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None
                    )
                except KeyError:
                    raise LineupOptimizerIncorrectCSV
                players.append(player)
        return players

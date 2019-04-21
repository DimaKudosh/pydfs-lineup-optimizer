import csv
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site
from pydfs_lineup_optimizer.sites.draftkings.classic.importer import DraftKingsCSVImporter


@SitesRegistry.register_csv_importer
class DraftKingsCaptainModeCSVImporter(DraftKingsCSVImporter):  # pragma: nocover
    site = Site.DRAFTKINGS_CAPTAIN_MODE

    def _row_to_player(self, row):
        try:
            fppg_multiplier = 1.5 if row['Roster Position'] == 'CPT' else 1
            max_exposure = row.get('Max Exposure', '').replace('%', '')
            name = row['Name'].split()
            player = Player(
                row['ID'],
                name[0],
                name[1] if len(name) > 1 else '',
                row['Roster Position'].split('/'),
                row['TeamAbbrev'],
                float(row['Salary']),
                float(row['AvgPointsPerGame']) * fppg_multiplier,
                max_exposure=float(max_exposure) if max_exposure else None
            )
        except KeyError:
            raise LineupOptimizerIncorrectCSV
        return player

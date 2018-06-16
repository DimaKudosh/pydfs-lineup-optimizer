import csv
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player


class DraftKingsCSVImporter(CSVImporter):
    def import_players(self):  # pragma: no cover
        players = []
        with open(self.filename, 'r') as csvfile:
            csv_data = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csv_data:
                try:
                    max_exposure = row.get('Max Exposure')
                    name = row['Name'].split()
                    player = Player(
                        row['ID'],
                        name[0],
                        name[1] if len(name) > 1 else '',
                        row['Position'].split('/'),
                        row['TeamAbbrev'],
                        float(row['Salary']),
                        float(row['AvgPointsPerGame']),
                        max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None
                    )
                except KeyError:
                    raise LineupOptimizerIncorrectCSV
                players.append(player)
        return players

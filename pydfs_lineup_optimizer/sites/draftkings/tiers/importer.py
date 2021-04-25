from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.sites.draftkings.classic.importer import DraftKingsCSVImporter


class DraftKingsTiersCSVImporter(DraftKingsCSVImporter):  # pragma: nocover
    def _row_to_player(self, row):
        try:
            name = row['Name'].split(maxsplit=1)
            player = Player(
                row['ID'],
                name[0],
                name[1] if len(name) > 1 else '',
                row['Roster Position'].split('/'),
                row['TeamAbbrev'],
                0,
                float(row['AvgPointsPerGame']),
                game_info=self._parse_game_info(row),
                original_positions=row['Position'].split('/'),
                **self.get_player_extra(row)
            )
        except KeyError:
            raise LineupOptimizerIncorrectCSV
        return player

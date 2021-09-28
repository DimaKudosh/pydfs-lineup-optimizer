from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.sites.draftkings.classic.importer import DraftKingsCSVImporter


class DraftKingsCaptainModeCSVImporter(DraftKingsCSVImporter):  # pragma: nocover
    def _row_to_player(self, row):
        try:
            fppg_multiplier = 1.5 if row['Roster Position'] == 'CPT' else 1
            name = row['Name'].split(maxsplit=1)
            player = Player(
                row['ID'],
                name[0],
                name[1] if len(name) > 1 else '',
                row['Roster Position'].split('/'),
                row['TeamAbbrev'],
                float(row['Salary']),
                float(row['AvgPointsPerGame']) * fppg_multiplier,
                game_info=self._parse_game_info(row),
                **self.get_player_extra(row)
            )
        except KeyError:
            raise LineupOptimizerIncorrectCSV
        return player

import csv
from itertools import islice
from datetime import datetime
from pytz import timezone
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.player import Player, LineupPlayer, GameInfo
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site


@SitesRegistry.register_csv_importer
class DraftKingsCSVImporter(CSVImporter):  # pragma: nocover
    site = Site.DRAFTKINGS
    DEFAULT_TIMEZONE = 'US/Eastern'

    def _parse_game_info(self, row):
        game_info = row.get('Game Info')
        if not game_info:
            return
        if game_info in ('In Progress', 'Final'):
            return GameInfo(  # No game info provided, just mark game as started
                home_team='',
                away_team='',
                starts_at='',
                game_started=True)
        try:
            teams, date = game_info.split(' ', 1)
            away_team, home_team = teams.split('@')
            starts_at = datetime.strptime(date.replace(' ET', ''), '%m/%d/%Y %I:%M%p').\
                replace(tzinfo=timezone(self.DEFAULT_TIMEZONE))
            return GameInfo(
                home_team=home_team,
                away_team=away_team,
                starts_at=starts_at,
                game_started=False
            )
        except ValueError:
            return

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
                max_exposure=float(max_exposure) if max_exposure else None,
                game_info=self._parse_game_info(row),
            )
        except KeyError:
            raise LineupOptimizerIncorrectCSV
        return player

    def import_players(self):
        with open(self.filename, 'r') as csv_file:
            start_line = 0  # Find line with 'TeamAbbrev', that's where players data starts
            while True:
                line = csv_file.readline()
                if 'TeamAbbrev' in line:
                    csv_file.seek(0)
                    csv_data = csv.DictReader(islice(csv_file, start_line, None),
                                              skipinitialspace=True)
                    return [self._row_to_player(row) for row in csv_data]
                elif line == '':
                    raise LineupOptimizerIncorrectCSV
                else:
                    start_line += 1

    def import_lineups(self, players):
        with open(self.filename, 'r') as csv_file:
            lines = csv.reader(csv_file)
            try:
                header = next(lines)
                start_column = 4  # First 4 columns has info about tournament
                end_column = header.index('Instructions') - 1
            except (IndexError, ValueError):
                raise LineupOptimizerIncorrectCSV
            position_names = header[start_column:end_column]
            players_dict = {player.id: player for player in players}
            lineups = []
            for line in lines:
                if not line[0]:
                    break
                lineup_players = []
                for index, position in zip(range(start_column, end_column), position_names):
                    try:
                        player_data = line[index]
                        player_data = player_data.replace('(LOCKED)', '')  # Remove possible '(LOCKED)' substring
                        player_id = player_data.split('(')[1][:-1]
                    except IndexError:
                        raise LineupOptimizerIncorrectCSV
                    try:
                        player = players_dict[player_id]
                    except KeyError:
                        raise LineupOptimizerIncorrectCSV('Player not found in players pool')
                    lineup_players.append(LineupPlayer(player, position))
                lineups.append(Lineup(lineup_players))
            return lineups

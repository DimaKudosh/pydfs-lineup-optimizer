from itertools import chain
from pulp import *
from exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, LineupOptimizerIncorrectPositionName
from settings import BaseSettings
from player import Player
from lineup import Lineup
from utils import ratio


class LineupOptimizer(object):
    def __init__(self, settings):
        '''
        LineupOptimizer select the best lineup for daily fantasy sports.
        :type settings: BaseSettings
        '''
        self._players = []
        self._lineup = []
        self._available_positions = []
        self._available_teams = []
        self._set_settings(settings)
        self._removed_players = []
        self._search_threshold = 0.8

    @property
    def lineup(self):
        '''
        :rtype: list[Player]
        '''
        return self._lineup

    @property
    def budget(self):
        '''
        :rtype: int
        '''
        return self._budget

    @property
    def players(self):
        '''
        :rtype: list[Player]
        '''
        return [player for player in self._players if player not in self._removed_players and player not in self._lineup]

    @property
    def removed_players(self):
        '''
        :rtype: list[Player]
        '''
        return self._removed_players

    def _set_settings(self, settings=None):
        '''
        Set settings with daily fantasy sport site and kind of sport to optimizer.
        :type settings: BaseSettings
        '''
        if settings is not None:
            self._settings = settings
        self._budget = self._settings.budget
        self._total_players = self._settings.total_players
        self._positions = self._settings.positions.copy()
        self._no_position_players = self._settings.no_position_players
        self._available_positions = set(chain(*[pos for pos in self._settings.positions]))

    def reset_lineup(self):
        '''
        Reset current lineup.
        '''
        self._set_settings()
        self._lineup = []

    def load_players_from_CSV(self, filename):
        '''
        Load player list from CSV file with passed filename.
        Calls load_players_from_CSV method from _settings object.
        :type filename: str
        '''
        self._players = self._settings.load_players_from_CSV(filename)
        self._available_teams = set([p.team for p in self._players])

    def remove_player(self, player):
        '''
        Remove player from list for selecting players for lineup.
        :type player: Player
        '''
        self._removed_players.append(player)

    def restore_player(self, player):
        try:
            self._removed_players.remove(player)
        except ValueError:
            pass

    def _add_to_lineup(self, player):
        '''
        Adding player to lineup without checks
        :type player: Player
        '''
        self._lineup.append(player)
        self._total_players -= 1
        self._budget -= player.salary

    def find_players(self, name):
        '''
        Return list of players with similar name.
        :param name: str
        :return: List[Player]
        '''
        players = self.players
        possibilities = [(player, ratio(name, player.full_name)) for player in players]
        possibilities = filter(lambda pos: pos[1] >= self._search_threshold, possibilities)
        players = sorted(possibilities, key=lambda pos: -pos[1])
        return map(lambda p: p[0], players)

    def get_player_by_name(self, name):
        '''
        Return closest player with similar name or None.
        :param name: str
        :return: Player
        '''
        players = self.find_players(name)
        return players[0] if players else None

    def add_player_to_lineup(self, player):
        '''
        Force adding specified player to lineup.
        Return true if player successfully added to lineup.
        :type player: Player
        '''
        if player in self._lineup:
            raise LineupOptimizerException("This player already in your line up!")
        if not isinstance(player, Player):
            raise LineupOptimizerException("This function accept only Player objects!")
        try:
            if self._budget - player.salary < 0:
                raise LineupOptimizerException("Can't add this player to line up! Your team is over budget!")
            if self._total_players - 1 < 0:
                raise LineupOptimizerException("Can't add this player to line up! You already select all {} players!".
                                               format(len(self._lineup)))
            try:
                is_added = False

                def decrement_player_from_all_positions():
                    is_added = False
                    for key, value in self._positions.items():
                        if player.positions[0] in key and value >= 1:
                            self._positions[key] -= 1
                            is_added = True
                    return is_added

                try:
                    if self._positions[(player.positions[0], )] > 0:
                        is_added = decrement_player_from_all_positions()
                    else:
                        for key, value in self._positions.items():
                            if player.positions[0] in key and len(key) > 1:
                                for pos in key:
                                    if pos != player.positions[0]:
                                        try:
                                            value -= self._positions[(pos, )]
                                        except KeyError:
                                            pass
                                if value:
                                    is_added = decrement_player_from_all_positions()
                except KeyError:
                    pass
                if not is_added and self._no_position_players:
                    self._no_position_players -= 1
                    is_added = True
                if is_added:
                    self._add_to_lineup(player)
                else:
                    raise LineupOptimizerException("You're already select all {}'s".format(player.positions))
            except KeyError:
                raise LineupOptimizerException("This player has wrong position!")
        except ValueError:
            raise LineupOptimizerException("Player not in players list!")

    def remove_player_from_lineup(self, player):
        '''
        Remove specified player from lineup.
        :type player: Player
        '''
        if not isinstance(player, Player):
            raise LineupOptimizerException("This function accept only Player objects!")
        try:
            occupied_positions = {key: len(filter(lambda player: player.positions[0] in key, self._lineup))
                                  for key in self._positions.keys()}
            positions_difference = {key: occupied_positions[key] - self._settings.positions[key]
                                    for key in occupied_positions.keys()}
            try:
                if positions_difference[(player.positions[0], )] == 0:
                    for key in self._positions.keys():
                        if player.positions[0] in key:
                            self._positions[key] += 1
                else:
                    is_no_position_player = True
                    for key, value in positions_difference.items():
                        if player.positions[0] in key and value < 0:
                            is_no_position_player = False
                    if is_no_position_player:
                        self._no_position_players += 1
                    else:
                        for key in self._positions.keys():
                            if player.positions[0] in key and key != (player.positions[0], ):
                                self._positions[key] += 1
                self._lineup.remove(player)
                self._budget += player.salary
                self._total_players += 1
            except KeyError:
                pass
        except ValueError:
            raise LineupOptimizerException("Player not in line up!")

    def optimize(self, n=None,  teams=None, positions=None, with_injured=False):
        '''
        Select optimal lineup from players list.
        This method uses Mixed Integer Linear Programming method for evaluating best starting lineup.
        It's return generator. If you don't specify n it will return generator with all possible lineups started
        from highest fppg to lowest fppg.
        :type n: int
        :type teams: dict[str, int]
        :type positions: dict[str, int]
        :type with_injured: bool
        :rtype: List[Lineup]
        '''
        # check teams parameter
        if teams:
            if not isinstance(teams, dict) or not all([isinstance(team, str) for team in teams.keys()]) or \
                    not all([isinstance(num_of_players, int) for num_of_players in teams.values()]):
                raise LineupOptimizerException("Teams parameter must be dict where key is team name and value is number"
                                               " of players from specified team.")
            teams = {team.upper(): num_of_players for team, num_of_players in teams.items()}
            _teams = teams.keys()
            for team in _teams:
                if team not in self._available_teams:
                    raise LineupOptimizerIncorrectTeamName("{} is incorrect team name.".format(team))
        # check positions parameter
        if positions:
            if not isinstance(positions, dict) or \
                    not all([isinstance(position, str) for position in positions.keys()]) or \
                    not all([isinstance(num_of_players, int) for num_of_players in positions.values()]):
                raise LineupOptimizerException("Positions parameter must be dict where key is position name and value "
                                               "is number of players from specified position.")
            if sum(positions.values()) > self._no_position_players:
                raise LineupOptimizerException("You can specify only {} utils players.".
                                               format(self._no_position_players))
            positions = {position.upper(): num_of_players for position, num_of_players in positions.items()}
            _positions = positions.keys()
            for pos in _positions:
                if pos not in self._available_positions:
                    raise LineupOptimizerIncorrectPositionName("{} is incorrect position name.".format(pos))
        else:
            positions = {}

        # optimize
        current_max_points = 100000
        lineup_points = sum(player.fppg for player in self._lineup)
        if len(self._lineup) == self._settings.total_players:
            lineup = Lineup(self._lineup)
            yield lineup
            raise StopIteration()
        counter = 0
        while n is None or n > counter:
            players = [player for player in self._players
                       if player not in self._removed_players and player not in self._lineup
                       and isinstance(player, Player)]
            prob = LpProblem("Daily Fantasy Sports", LpMaximize)
            x = LpVariable.dicts(
                'table', players,
                lowBound=0,
                upBound=1,
                cat=LpInteger
            )
            prob += sum([player.fppg * x[player] for player in players])
            prob += sum([player.fppg * x[player] for player in players]) <= current_max_points
            prob += sum([player.salary * x[player] for player in players]) <= self._budget
            prob += sum([x[player] for player in players]) == self._total_players
            if not with_injured:
                prob += sum([x[player] for player in players if not player.is_injured]) == self._total_players
            for position, num in self._positions.items():
                addition = 0
                if len(position) == 1:
                    addition = positions.get(position[0], 0)
                prob += sum([x[player] for player in players if
                             any([player_position in position for player_position in player.positions])]) >= num + \
                                                                                                             addition
            if teams is not None:
                for key, value in teams.items():
                    prob += sum([x[player] for player in players if player.team == key]) == value
            prob.solve()
            if prob.status == 1:
                lineup_players = self._lineup[:]
                for player in players:
                    if x[player].value() == 1.0:
                        lineup_players.append(player)
                lineup = Lineup(lineup_players)
                current_max_points = lineup.fantasy_points_projection - lineup_points - 0.1
                yield lineup
                counter += 1
            else:
                raise LineupOptimizerException("Can't generate lineups")
        raise StopIteration()

from pulp import *
from exceptions import LineupOptimizerException
from settings import BaseSettings
from player import Player


class LineupOptimizer(object):
    def __init__(self, settings):
        '''
        LineupOptimizer select the best lineup for daily fantasy sports.
        :type settings: BaseSettings
        '''
        self._players = []
        self._lineup = []
        self._set_settings(settings)
        self._removed_players = []

    @property
    def lineup(self):
        '''
        :rtype: list[Player]
        '''
        return self._lineup

    @property
    def lineup_fantasy_points_projection(self):
        '''
        :rtype: int
        '''
        return sum(player.fppg for player in self._lineup)

    @property
    def lineup_salary_costs(self):
        '''
        :rtype: int
        '''
        return sum(player.salary for player in self._lineup)

    @property
    def players(self):
        '''
        :rtype: list[Player]
        '''
        return [player for player in self._players if player not in self._removed_players]

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

    def remove_player(self, player):
        '''
        Remove player from list for selecting players for lineup.
        :type player: Player
        '''
        self._removed_players.append(player)

    def add_player_to_lineup(self, player):
        '''
        Force adding specified player to lineup.
        Return true if player successfully added to lineup.
        :type player: Player
        '''
        if player in self._lineup:
            raise LineupOptimizerException("This player already in your line up!")
        try:
            if self._budget - player.salary < 0:
                raise LineupOptimizerException("Can't add this player to line up! Your team is over budget!")
            if self._total_players - 1 < 0:
                raise LineupOptimizerException("Can't add this player to line up! You already select all {} players!".
                                               format(self._total_players))
            position = (player.position, )
            try:
                if self._positions[position] >= 1:
                    self._positions[position] -= 1
                for key, value in self._positions.items():
                    if position[0] in key and key != position and value >= 1:
                        self._lineup.append(player)
                        self._positions[key] -= 1
                        self._total_players -= 1
                        self._budget -= player.salary
                        return
                raise LineupOptimizerException("You're already select all {}'s".format(player.position))
            except KeyError:
                raise LineupOptimizerException("This player has wrong position!")
        except ValueError:
            raise LineupOptimizerException("Player not in players list!")

    def remove_player_from_lineup(self, player):
        '''
        Remove specified player from lineup.
        :type player: Player
        '''
        try:
            self._lineup.remove(player)
            self._budget += player.salary
            self._total_players += 1
            position = (player.position, )
            for key in self._positions.keys():
                if position[0] in key and key != position:
                    self._positions[key] += 1
                    if self._positions[key] > self._settings.positions[key] - self._settings.positions[position]:
                        self._positions[position] += 1
        except ValueError, KeyError:
            raise LineupOptimizerException("Player not in line up!")

    def optimize(self, teams=None, positions=None):
        '''
        Select optimal lineup from players list.
        This method uses Mixed Integer Linear Programming method for evaluating best starting lineup.
        :type teams: dict[str, int]
        :type positions: dict[str, int]
        '''
        players = [player for player in self._players if player not in self._removed_players]
        prob = LpProblem("Daily Fantasy Sports", LpMaximize)
        x = LpVariable.dicts(
            'table', players,
            lowBound = 0,
            upBound = 1,
            cat = LpInteger
        )
        prob += sum([player.fppg * x[player] for player in players])
        prob += sum([player.salary * x[player] for player in players]) <= self._budget
        prob += sum([x[player] for player in players]) == self._total_players
        prob += sum([x[player] for player in players if not player.is_injured]) == self._total_players
        for position, num in self._positions.items():
            prob += sum([x[player] for player in players if player.position in position]) >= num
        if teams is not None:
            for key, value in teams.items():
                prob += sum([x[player] for player in players if player.team == key]) == value
        if positions is not None:
            for key, value in positions.items():
                prob += sum([x[player] for player in players if player.position == key]) == value
        prob.solve()
        if prob.status == 1:
            for player in players:
                if x[player].value() == 1.0:
                    self._total_players -= 1
                    self._budget -= player.salary
                    for key, value in self._positions.items():
                        if player.position in key and value:
                            self._positions[key] -= 1
                    self._lineup.append(player)
        else:
            raise LineupOptimizerException("Can't create optimal lineup! Wrong input data!")

    def print_lineup(self):
        '''
        Represent current lineup as table with players and output it to console.
        '''
        res = '\n'.join([str(index + 1) + ". " + str(player) for index, player in enumerate(self._lineup)])
        res += '\nFantasy Points ' + str(sum(player.fppg for player in self._lineup))
        res += '\nSalary ' + str(sum(player.salary for player in self._lineup))
        print(res)

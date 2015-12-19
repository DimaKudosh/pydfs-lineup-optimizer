from pulp import *
import csv
from player import Player


class LineupOptimizer:
    def __init__(self, settings):
        '''
        :param settings: Settings
        '''
        self._players = []
        self._settings = settings
        self._lineup = []
        self._set_settings()
        self._removed_players = []

    def _set_settings(self):
        self._budget = self._settings.budget
        self._total_players = self._settings.total_players
        self._positions = self._settings.positions.copy()

    def reset_lineup(self):
        self._set_settings()
        self._lineup = []

    def load_players_from_CSV(self, filename):
        self._players = self._settings.load_players_from_CSV(filename)

    def remove_player(self, player):
        '''

        :param player: Player
        '''
        self._removed_players.append(player)

    def add_player_to_lineup(self, player):
        '''
        Return true if player successfully added to lineup.
        :param player: Player
        :return: bool
        '''
        if player in self._lineup:
            print("This player already in your line up!")
            return False
        try:
            if self._budget - player.salary < 0:
                print("Can't add this player to line up! Your team is over budget!")
                return False
            if self._total_players - 1 < 0:
                print("Can't add this player to line up! You already select all {} players!".format(self._total_players))
                return False
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
                        return True
                print("You're already select all {}'s".format(player.position))
                return False
            except KeyError:
                print("This player has wrong position!")
                return False
        except ValueError:
            print("Player not in players list!")
            return False

    def remove_player_from_lineup(self, player):
        '''

        :param player: Player
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
            print("Player not in line up!")

    def optimize(self):
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

    def print_lineup(self):
        res = '\n'.join([str(index + 1) + ". " + str(player) for index, player in enumerate(self._lineup)])
        res += '\nFantasy Points ' + str(sum(player.fppg for player in self._lineup))
        res += '\nSalary ' + str(sum(player.salary for player in self._lineup))
        print(res)

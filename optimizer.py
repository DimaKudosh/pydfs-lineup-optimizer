from pulp import *
import csv
from player import Player


class Optimizer:
    def __init__(self, settings):
        '''

        :param players: list[Player]
        :param settings: Settings
        :return:
        '''
        self._players = []
        self._settings = settings
        self._lineup = []
        self._budget = settings.budget
        self._total_players = settings.total_players
        self._positions = settings.positions

    def load_players_from_CSV(self, filename):
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                player = Player(
                    row["First Name"],
                    row["Last Name"],
                    row["Position"],
                    row["Team"],
                    float(row["Salary"]),
                    float(row["FPPG"]),
                    True if row["Injury Status"].strip() else False
                )
                self._players.append(player)

    def optimize(self):
        prob = LpProblem("Daily Fantasy Sports", LpMaximize)
        x = LpVariable.dicts(
            'table', self._players,
            lowBound = 0,
            upBound = 1,
            cat = LpInteger
        )
        prob += sum([player.fppg * x[player] for player in self._players])
        prob += sum([player.salary * x[player] for player in self._players]) <= self._budget
        prob += sum([x[player] for player in self._players]) == self._total_players
        prob += sum([x[player] for player in self._players if not player.is_injured]) == self._total_players
        for position, num in self._positions.items():
            prob += sum([x[player] for player in self._players if player.position in position]) >= num
        prob.solve()
        for player in self._players:
            if x[player].value() == 1.0:
                self._lineup.append(player)

    def print_lineup(self):
        res = '\n'.join([str(index + 1) + ". " + str(player) for index, player in enumerate(self._lineup)])
        res += '\nFantasy Points ' + str(sum(player.fppg for player in self._lineup))
        res += '\nSalary ' + str(sum(player.salary for player in self._lineup))
        print(res)

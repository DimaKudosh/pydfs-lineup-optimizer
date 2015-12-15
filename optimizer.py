from pulp import *
import csv
from player import Player


class Optimizer:
    def __init__(self, players, settings):
        '''

        :param players: list[Player]
        :param settings:
        :return:
        '''
        self.players = []
        self.settings = settings
        self._lineup = []
        #self.budget = settings.budget

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
                self.players.append(player)

    def optimize(self):
        prob = LpProblem("Daily Fantasy Sports", LpMaximize)
        x = LpVariable.dicts('table', self.players,
                            lowBound = 0,
                            upBound = 1,
                            cat = LpInteger)
        prob += sum([player.fppg * x[player] for player in self.players])
        prob += sum([player.salary * x[player] for player in self.players]) <= 200
        prob += sum([x[player] for player in self.players]) == 8
        prob += sum([x[player] for player in self.players if player.position == 'PG']) >= 1
        prob += sum([x[player] for player in self.players if player.position == 'SG']) >= 1
        prob += sum([x[player] for player in self.players if player.position == 'SF']) >= 1
        prob += sum([x[player] for player in self.players if player.position == 'PF']) >= 1
        prob += sum([x[player] for player in self.players if player.position == 'C']) >= 1
        prob += sum([x[player] for player in self.players if 'G' in player.position]) >= 3
        prob += sum([x[player] for player in self.players if 'F' in player.position]) >= 3
        prob += sum([x[player] for player in self.players if not player.is_injured]) == 8
        prob.solve()
        for player in self.players:
            if x[player].value() == 1.0:
                self._lineup.append(player)

    def print_lineup(self):
        res = '\n'.join([str(index + 1) + ". " + str(player) for index, player in enumerate(self._lineup)])
        res += '\nFantasy Points ' + str(sum(player.fppg for player in self._lineup))
        res += '\nSalary ' + str(sum(player.salary for player in self._lineup))
        print(res)


optimizer = Optimizer([], None)
optimizer.load_players_from_CSV("nba_sample.csv")
optimizer.optimize()
optimizer.print_lineup()

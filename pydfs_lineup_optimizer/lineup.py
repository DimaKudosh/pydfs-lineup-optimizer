from .player import Player


class Lineup:
    def __init__(self, players):
        '''
        :param players: List[Player]
        '''
        self.players = players

    def __str__(self):
        res = '\n'.join([str(index + 1) + ". " + str(player) for index, player in enumerate(self.players)])
        res += '\nFantasy Points ' + str(sum(player.fppg for player in self.players))
        res += '\nSalary ' + str(sum(player.salary for player in self.players))
        return res

    @property
    def lineup(self):
        '''
        :rtype: list[Player]
        '''
        return self.players

    @property
    def fantasy_points_projection(self):
        '''
        :rtype: int
        '''
        return sum(player.fppg for player in self.players)

    @property
    def salary_costs(self):
        '''
        :rtype: int
        '''
        return sum(player.salary for player in self.players)

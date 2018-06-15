from typing import List
from pydfs_lineup_optimizer.player import LineupPlayer


class Lineup(object):
    def __init__(self, players):
        # type: (List[LineupPlayer]) -> None
        self.players = players

    def __iter__(self):
        return iter(self.players)

    def __contains__(self, item):
        return item in self.players

    def __str__(self):
        res = ''
        for index, player in enumerate(self.players, start=1):
            res += '{0:>2}. {1:<5} {2:<30}{3:<6}{4:<15}{5:<8}{6:<10}\n'.format(
                index,
                player.lineup_position,
                player.full_name,
                '/'.join(player.positions),
                player.team,
                round(player.fppg, 3),
                str(player.salary) + '$',
            )
        res += '\nFantasy Points ' + str(self.fantasy_points_projection)
        res += '\nSalary ' + str(self.salary_costs)
        return res

    def __repr__(self):
        return 'Lineup: projection %s, budget %s' % (self.fantasy_points_projection, self.salary_costs)

    @property
    def lineup(self):
        # type: () -> List[LineupPlayer]
        return self.players

    @property
    def fantasy_points_projection(self):
        # type: () -> int
        return round(sum(player.fppg for player in self.players), 3)

    @property
    def salary_costs(self):
        # type: () -> int
        return sum(player.salary for player in self.players)

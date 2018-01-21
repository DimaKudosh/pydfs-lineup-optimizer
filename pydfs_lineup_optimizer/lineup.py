from .player import Player


class LineupPlayer(object):
    __slots__ = ['_player', 'lineup_position']

    def __init__(self, player, lineup_position):
        """
        :type player: Player
        :type lineup_position: str
        """
        self._player = player
        self.lineup_position = lineup_position

    def __getattr__(self, attr_name):
        return getattr(self._player, attr_name)

    def __eq__(self, other):
        if isinstance(other, Player):
            return self._player == other
        elif isinstance(other, LineupPlayer):
            return self._player == other._player
        return NotImplemented

    def __str__(self):
        return str(self._player)


class Lineup(object):
    def __init__(self, players):
        """
        :type players: list[LineupPlayer]
        """
        self.players = players

    def __iter__(self):
        return iter(self.players)

    def __contains__(self, item):
        return item in self.players

    def __str__(self):
        res = ''
        for index, player in enumerate(self.players, start=1):
            res += '{0}. {1:<5} {2:<30}{3:<6}{4:<15}{5:<8}{6:<10}\n'.format(
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
        """
        :rtype: list[LineupPlayer]
        """
        return self.players

    @property
    def fantasy_points_projection(self):
        """
        :rtype: int
        """
        return round(sum(player.fppg for player in self.players), 3)

    @property
    def salary_costs(self):
        """
        :rtype: int
        """
        return sum(player.salary for player in self.players)

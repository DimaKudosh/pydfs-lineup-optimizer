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
        return self._player == other._player

    def __str__(self):
        return str(self._player)


class Lineup(object):
    def __init__(self, players):
        """
        :type players: list[LineupPlayer]
        """
        self.players = players

    def __str__(self):
        res = ''
        for index, player in enumerate(self.players):
            res += "{0}. {1} {2}{3}{4}{5}{6}".format(
                index,
                '{:<5}'.format(player.lineup_position),
                "{:<30}".format(player.full_name),
                "{:<5}".format('/'.join(player.positions)),
                "{:<15}".format(player.team),
                "{:<8}".format(str(round(player.fppg, 3))),
                "{:<10}".format(str(player.salary) + '$')
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
        return sum(player.fppg for player in self.players)

    @property
    def salary_costs(self):
        """
        :rtype: int
        """
        return sum(player.salary for player in self.players)

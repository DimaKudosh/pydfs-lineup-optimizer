from __future__ import division


class Player(object):
    def __init__(self, player_id,  first_name, last_name, positions, team, salary, fppg, is_injured=False,
                 max_exposure=None):
        self.id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.positions = positions
        self.team = team.upper()
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured
        self._max_exposure = None
        self.max_exposure = max_exposure

    def __str__(self):
        return '%s %s (%s)' % (self.full_name, '/'.join(self.positions), self.team)

    def __repr__(self):
        return str(self)

    @property
    def max_exposure(self):
        return self._max_exposure

    @max_exposure.setter
    def max_exposure(self, max_exposure):
        self._max_exposure = max_exposure / 100 if max_exposure and max_exposure > 1 else max_exposure

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def efficiency(self):
        return round(self.fppg / self.salary, 2)

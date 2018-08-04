from collections import namedtuple


LineupPosition = namedtuple('LineupPosition', ['name', 'positions'])


class BaseSettings(object):
    site = None
    sport = None
    budget = 0
    positions = []
    max_from_one_team = None

    @classmethod
    def get_total_players(cls):
        return len(cls.positions)

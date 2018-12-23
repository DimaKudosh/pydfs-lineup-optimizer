from collections import namedtuple
from pydfs_lineup_optimizer.lineup_printer import LineupPrinter


LineupPosition = namedtuple('LineupPosition', ['name', 'positions'])


class BaseSettings(object):
    site = None
    sport = None
    budget = 0
    positions = []
    max_from_one_team = None
    lineup_printer = LineupPrinter

    @classmethod
    def get_total_players(cls):
        return len(cls.positions)

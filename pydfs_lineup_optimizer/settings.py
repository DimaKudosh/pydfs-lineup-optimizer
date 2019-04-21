from collections import namedtuple
from typing import Optional, Type, List
from pydfs_lineup_optimizer.lineup_printer import LineupPrinter, BaseLineupPrinter


LineupPosition = namedtuple('LineupPosition', ['name', 'positions'])


class BaseSettings(object):
    site = None  # type: str
    sport = None  # type: str
    budget = 0  # type: float
    positions = []  # type: List[LineupPosition]
    max_from_one_team = None  # type: Optional[int]
    lineup_printer = LineupPrinter  # type: Type[BaseLineupPrinter]

    @classmethod
    def get_total_players(cls):
        # type: () -> int
        return len(cls.positions)

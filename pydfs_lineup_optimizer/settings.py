from collections import namedtuple
from typing import Optional, Type, List, TYPE_CHECKING
from pydfs_lineup_optimizer.lineup_printer import LineupPrinter, BaseLineupPrinter


if TYPE_CHECKING:  # pragma: no cover
    from pydfs_lineup_optimizer.rules import OptimizerRule


LineupPosition = namedtuple('LineupPosition', ['name', 'positions'])


class BaseSettings(object):
    site = None  # type: str
    sport = None  # type: str
    budget = 0  # type: float
    positions = []  # type: List[LineupPosition]
    max_from_one_team = None  # type: Optional[int]
    lineup_printer = LineupPrinter  # type: Type[BaseLineupPrinter]
    extra_rules = []  # type: List[Type['OptimizerRule']]

    @classmethod
    def get_total_players(cls):
        # type: () -> int
        return len(cls.positions)

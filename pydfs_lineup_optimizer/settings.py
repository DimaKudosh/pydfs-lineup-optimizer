from typing import Optional, Type, List, Sequence, TYPE_CHECKING
from pydfs_lineup_optimizer.lineup_printer import LineupPrinter, BaseLineupPrinter
from pydfs_lineup_optimizer.constants import PlayerRank


if TYPE_CHECKING:  # pragma: no cover
    from pydfs_lineup_optimizer.rules import OptimizerRule
    from pydfs_lineup_optimizer.lineup_importer import CSVImporter


class LineupPosition:
    def __init__(self, name: str, positions: Sequence[str], for_rank: PlayerRank = PlayerRank.REGULAR):
        self.name = name
        self.positions = positions
        self.for_rank = for_rank


class BaseSettings:
    site = None  # type: str
    sport = None  # type: str
    budget = 0  # type: float
    positions = []  # type: List[LineupPosition]
    max_from_one_team = None  # type: Optional[int]
    min_teams = None  # type: Optional[int]
    total_teams_exclude_positions = []  # type: List[str]
    lineup_printer = LineupPrinter  # type: Type[BaseLineupPrinter]
    extra_rules = []  # type: List[Type['OptimizerRule']]
    csv_importer = None  # type: Type['CSVImporter']

    @classmethod
    def get_total_players(cls) -> int:
        return len(cls.positions)

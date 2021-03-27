from typing import Optional, Dict, List, Type, Iterable
from itertools import chain
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.exposure_strategy import BaseExposureStrategy, TotalExposureStrategy


class OptimizationContext:
    def __init__(
            self,
            total_lineups: int,
            players: List[Player],
            max_exposure: Optional[float] = None,
            randomness: bool = False,
            existed_lineups: List[Lineup] = None,
            exposure_strategy: Type[BaseExposureStrategy] = TotalExposureStrategy,
            exclude_lineups: Optional[Iterable[Lineup]] = None,
    ):
        self.total_lineups = total_lineups
        self.players = players
        self.remaining_lineups = total_lineups
        self.max_exposure = max_exposure
        self.randomness = randomness
        self.existed_lineups = existed_lineups or []
        self.exclude_lineups = exclude_lineups or []
        self.lineups = []  # type: List[Lineup]
        self.players_used_fppg = {}  # type: Dict[Player, float]
        self.exposure_strategy = exposure_strategy

    def add_lineup(self, lineup: Lineup) -> None:
        self.lineups.append(lineup)
        self.remaining_lineups -= 1
        self.players_used_fppg = {}

    def get_lineups(self, with_excluded: bool = True) -> Iterable:
        if with_excluded and self.exclude_lineups:
            return list(chain(self.exclude_lineups, self.lineups))
        return self.lineups

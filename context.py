from typing import List, Optional
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup


class OptimizationContext:
    def __init__(
            self,
            total_lineups: int,
            players: List[Player],
            max_exposure: Optional[float] = None,
            randomness: bool = False,
            with_injured: bool = False,
            existed_lineups: List[Lineup] = None,
    ):
        self.total_lineups = total_lineups
        self.players = players
        self.remaining_lineups = total_lineups
        self.max_exposure = max_exposure
        self.randomness = randomness
        self.with_injured = with_injured
        self.existed_lineups = existed_lineups or []
        self.lineups = []

    def add_lineup(self, lineup: Lineup) -> None:
        self.lineups.append(lineup)
        self.remaining_lineups -= 1

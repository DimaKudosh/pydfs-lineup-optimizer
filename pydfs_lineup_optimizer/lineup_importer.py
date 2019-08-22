from typing import List, Dict, Any, Optional
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup


class CSVImporter(object):
    site = None  # type: str

    def __init__(self, filename):
        # type: (str) -> None
        self.filename = filename

    def import_players(self):  # pragma: no cover
        # type: () -> List[Player]
        raise NotImplementedError

    def import_lineups(self, players):  # pragma: no cover
        # type: (List[Player]) -> List[Lineup]
        raise NotImplementedError

    @staticmethod
    def _parse_exposure(exposure):
        # type: (Optional[str]) -> Optional[float]
        exposure = (exposure or '').replace('%', '')
        return float(exposure) if exposure else None

    @classmethod
    def get_player_extra(cls, row):
        # type: (Dict[str, str]) -> Dict[str, Any]
        roster_order = row.get('Roster Order')
        return {
            'max_exposure': cls._parse_exposure(row.get('Max Exposure')),
            'min_exposure': cls._parse_exposure(row.get('Min Exposure')),
            'roster_order': int(roster_order) if roster_order else None,
            'projected_ownership': cls._parse_exposure(row.get('Projected Ownership')),
        }

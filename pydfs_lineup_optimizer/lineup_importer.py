from typing import List, Dict, Any, Optional
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup


class CSVImporter:
    def __init__(self, filename: str):
        self.filename = filename

    def import_players(self) -> List[Player]:  # pragma: no cover
        raise NotImplementedError

    def import_lineups(self, players: List[Player]) -> List[Lineup]:  # pragma: no cover
        pass

    @staticmethod
    def _parse_exposure(exposure: Optional[str]) -> Optional[float]:
        exposure = (exposure or '').replace('%', '')
        return float(exposure) if exposure else None

    @classmethod
    def get_player_extra(cls, row: Dict[str, str]) -> Dict[str, Any]:
        roster_order = row.get('Roster Order')
        fppg_floor = row.get('Projection Floor')
        fppg_ceil = row.get('Projection Ceil')
        return {
            'max_exposure': cls._parse_exposure(row.get('Max Exposure')),
            'min_exposure': cls._parse_exposure(row.get('Min Exposure')),
            'roster_order': int(roster_order) if roster_order else None,
            'projected_ownership': cls._parse_exposure(row.get('Projected Ownership')),
            'min_deviation': cls._parse_exposure(row.get('Min Deviation')),
            'max_deviation': cls._parse_exposure(row.get('Max Deviation')),
            'is_confirmed_starter': bool(row.get('Confirmed Starter')),
            'fppg_floor': float(fppg_floor) if fppg_floor else None,
            'fppg_ceil': float(fppg_ceil) if fppg_ceil else None,
        }

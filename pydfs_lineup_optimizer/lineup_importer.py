from typing import List, Dict, Any, Optional
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.exceptions import LineupOptimizerIncorrectCSV


class CSVImporter:
    def __init__(self, filename: str):
        self.filename = filename

    def import_players(self) -> List[Player]:  # pragma: no cover
        raise NotImplementedError

    def import_lineups(self, players: List[Player]) -> List[Lineup]:  # pragma: no cover
        pass

    @staticmethod
    def _parse_percents(value: Optional[str]) -> Optional[float]:
        value = value or ''
        if not value.strip():
            return None
        try:
            parsed_value = float(value.replace('%', '').strip())
            return parsed_value / 100 if parsed_value > 1 else parsed_value
        except ValueError:
            raise LineupOptimizerIncorrectCSV('Can\'t parse percents value, got %s' % value)

    @classmethod
    def get_player_extra(cls, row: Dict[str, str]) -> Dict[str, Any]:
        roster_order = row.get('Roster Order')
        fppg_floor = row.get('Projection Floor')
        fppg_ceil = row.get('Projection Ceil')
        return {
            'max_exposure': cls._parse_percents(row.get('Max Exposure')),
            'min_exposure': cls._parse_percents(row.get('Min Exposure')),
            'roster_order': int(roster_order) if roster_order else None,
            'projected_ownership': cls._parse_percents(row.get('Projected Ownership')),
            'min_deviation': cls._parse_percents(row.get('Min Deviation')),
            'max_deviation': cls._parse_percents(row.get('Max Deviation')),
            'is_confirmed_starter': bool(row.get('Confirmed Starter')),
            'fppg_floor': float(fppg_floor) if fppg_floor else None,
            'fppg_ceil': float(fppg_ceil) if fppg_ceil else None,
            'progressive_scale': cls._parse_percents(row.get('Progressive Scale')),
        }

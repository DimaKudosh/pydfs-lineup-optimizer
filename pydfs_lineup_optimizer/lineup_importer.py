from typing import List, Dict, Any
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
    def get_player_extra(row):
        # type: (Dict[str, str]) -> Dict[str, Any]
        max_exposure = (row.get('Max Exposure') or '').replace('%', '')
        roster_order = row.get('Roster Order')
        return {
            'max_exposure': float(max_exposure) if max_exposure else None,
            'roster_order': int(roster_order) if roster_order else None,
        }

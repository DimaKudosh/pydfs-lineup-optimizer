from typing import List
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

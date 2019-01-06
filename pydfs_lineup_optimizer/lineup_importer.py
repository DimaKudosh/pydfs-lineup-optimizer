from typing import List
from pydfs_lineup_optimizer.player import Player


class Importable(object):
    site = None  # type: str

    def import_players(self):  # pragma: no cover
        # type: () -> List[Player]
        raise NotImplementedError


class CSVImporter(Importable):
    def __init__(self, filename):
        # type: (str) -> None
        self.filename = filename

    def import_players(self):  # pragma: no cover
        raise NotImplementedError

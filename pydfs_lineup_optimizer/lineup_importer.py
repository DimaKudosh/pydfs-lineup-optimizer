from typing import List
from pydfs_lineup_optimizer.player import Player


class Importable(object):
    def import_players(self):
        # type: () -> List[Player]
        raise NotImplementedError


class CSVImporter(Importable):
    def __init__(self, filename):
        # type: (str) -> None
        self.filename = filename

    def import_players(self):
        raise NotImplementedError

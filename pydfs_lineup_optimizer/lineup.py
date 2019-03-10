from typing import List, Type
from pydfs_lineup_optimizer.player import LineupPlayer
from pydfs_lineup_optimizer.lineup_printer import BaseLineupPrinter, LineupPrinter


class Lineup(object):
    def __init__(self, players, printer=LineupPrinter):
        # type: (List[LineupPlayer], Type[BaseLineupPrinter]) -> None
        self.players = players
        self.printer = printer()

    def __iter__(self):
        return iter(self.players)

    def __contains__(self, item):
        return item in self.players

    def __str__(self):
        return self.printer.print_lineup(self)

    def __repr__(self):
        return 'Lineup: projection %s, budget %s' % (self.fantasy_points_projection, self.salary_costs)

    @property
    def lineup(self):
        # type: () -> List[LineupPlayer]
        return self.players

    @property
    def fantasy_points_projection(self):
        # type: () -> float
        return round(sum(player.fppg for player in self.players), 3)

    @property
    def salary_costs(self):
        # type: () -> int
        return sum(player.salary for player in self.players)

    def get_unswappable_players(self):
        # type: () -> List[LineupPlayer]
        return [player for player in self.players if player.is_game_started]

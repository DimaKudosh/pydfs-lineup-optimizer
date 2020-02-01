from pydfs_lineup_optimizer.version import __version__
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName, LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.sites import SitesRegistry
from pydfs_lineup_optimizer.lineup_exporter import CSVLineupExporter, FantasyDraftCSVLineupExporter
from pydfs_lineup_optimizer.tz import set_timezone


__all__ = [
    'get_optimizer', 'Site', 'Sport', 'Player', 'LineupOptimizerException', 'LineupOptimizerIncorrectTeamName',
    'LineupOptimizerIncorrectPositionName', 'LineupOptimizerIncorrectCSV', 'LineupOptimizer', 'Lineup',
    'CSVLineupExporter', 'set_timezone', 'FantasyDraftCSVLineupExporter',
]


def get_optimizer(site: str, sport: str, **kwargs) -> LineupOptimizer:
    return LineupOptimizer(SitesRegistry.get_settings(site, sport), **kwargs)

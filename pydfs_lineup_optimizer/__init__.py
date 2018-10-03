from pydfs_lineup_optimizer.version import __version__
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName, LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.sites import SitesRegistry
from pydfs_lineup_optimizer.lineup_exporter import CSVLineupExporter


def get_optimizer(site, sport):
    # type: (str, str) -> LineupOptimizer
    return LineupOptimizer(SitesRegistry.get_settings(site, sport))

__version__ = '2.0.2'

from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName, LineupOptimizerIncorrectCSV
from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.sites import SETTINGS_MAPPING, CSV_IMPORTERS_MAPPING
from pydfs_lineup_optimizer.lineup_exporter import CSVLineupExporter


def get_optimizer(site, sport):
    # type: (str, str) -> LineupOptimizer
    try:
        return LineupOptimizer(SETTINGS_MAPPING[site][sport], CSV_IMPORTERS_MAPPING[site])
    except KeyError:
        raise NotImplementedError

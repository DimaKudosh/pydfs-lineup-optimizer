from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import DropLowestLineupPrinter


class FanDuelSettings(BaseSettings):
    site = Site.FANDUEL
    budget = 60000
    max_from_one_team = 4


@SitesRegistry.register_settings
class FanDuelBasketballSettings(FanDuelSettings):
    sport = Sport.BASKETBALL
    lineup_printer = DropLowestLineupPrinter
    positions = [
        LineupPosition('PG', ('PG', )),
        LineupPosition('PG', ('PG', )),
        LineupPosition('SG', ('SG', )),
        LineupPosition('SG', ('SG', )),
        LineupPosition('SF', ('SF', )),
        LineupPosition('SF', ('SF', )),
        LineupPosition('PF', ('PF', )),
        LineupPosition('PF', ('PF', )),
        LineupPosition('C', ('C', )),
    ]


@SitesRegistry.register_settings
class FanDuelFootballSettings(FanDuelSettings):
    sport = Sport.FOOTBALL
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('TE', ('TE', )),
        LineupPosition('D', ('D', )),
        LineupPosition('FLEX', ('RB', 'WR', 'TE')),
    ]


@SitesRegistry.register_settings
class FanDuelHockeySettings(FanDuelSettings):
    sport = Sport.HOCKEY
    budget = 55000
    positions = [
        LineupPosition('C', ('C', )),
        LineupPosition('C', ('C', )),
        LineupPosition('W', ('W', )),
        LineupPosition('W', ('W', )),
        LineupPosition('W', ('W', )),
        LineupPosition('W', ('W', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('G', ('G', )),
    ]


@SitesRegistry.register_settings
class FanDuelBaseballSettings(FanDuelSettings):
    max_from_one_team = 5
    sport = Sport.BASEBALL
    budget = 35000
    positions = [
        LineupPosition('P', ('P',)),
        LineupPosition('C/1B', ('C', '1B')),
        LineupPosition('2B', ('2B',)),
        LineupPosition('3B', ('3B',)),
        LineupPosition('SS', ('SS',)),
        LineupPosition('OF', ('OF',)),
        LineupPosition('OF', ('OF',)),
        LineupPosition('OF', ('OF',)),
        LineupPosition('UTIL', ('1B', '2B', '3B', 'SS', 'C', 'OF')),
    ]


@SitesRegistry.register_settings
class FanDuelWnbaSettings(FanDuelSettings):
    sport = Sport.WNBA
    budget = 40000
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
    ]

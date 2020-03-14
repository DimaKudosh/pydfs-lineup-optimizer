from typing import List, Type, Optional
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import IndividualSportLineupPrinter
from pydfs_lineup_optimizer.rules import OptimizerRule, FANDUELBaseballRosterRule


class FANDUELSettings(BaseSettings):
    site = Site.FANDUEL
    budget = 60000
    max_from_one_team = 8  # type: Optional[int]
    min_teams = 1


@SitesRegistry.register_settings
class FANDUELBasketballSettings(FANDUELSettings):
    sport = Sport.BASKETBALL
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
class FANDUELFOOTBALLSettings(FANDUELSettings):
    sport = Sport.FOOTBALL
    positions = [
        LineupPosition('HK', ('HK', )),
        LineupPosition('FWD', ('FWD', )),
        LineupPosition('FWD', ('FWD', )),
        LineupPosition('FWD', ('FWD', )),
        LineupPosition('FWD', ('FWD', )),
        LineupPosition('HF', ('HF', )),
        LineupPosition('OB', ('OB', )),
        LineupPosition('OB', ('OB', )),
        LineupPosition('OB', ('OB', )),
    ]


@SitesRegistry.register_settings
class FANDUELHockeySettings(FANDUELSettings):
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
class FANDUELBaseballSettings(FANDUELSettings):
    max_from_one_team = 5
    sport = Sport.BASEBALL
    budget = 35000
    extra_rules = [FANDUELBaseballRosterRule]
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
class FANDUELWnbaSettings(FANDUELSettings):
    sport = Sport.WNBA
    budget = 40000
    extra_rules = []  # type: List[Type[OptimizerRule]]
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
    ]


@SitesRegistry.register_settings
class FANDUELGolfSettings(FANDUELSettings):
    sport = Sport.GOLF
    max_from_one_team = None
    extra_rules = []  # type: List[Type[OptimizerRule]]
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
    ]

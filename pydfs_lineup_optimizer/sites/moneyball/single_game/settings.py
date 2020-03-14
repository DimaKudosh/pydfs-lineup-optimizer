from typing import List, Type
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.rules import OptimizerRule, FANDUELSingleGameMVPRule, FANDUELSingleGameMaxQBRule, \
    FANDUELSingleGameBasketballRule


class FANDUELSingleGameSettings(BaseSettings):
    site = Site.FANDUEL_SINGLE_GAME
    budget = 60000
    max_from_one_team = 9
    extra_rules = [FANDUELSingleGameMVPRule]  # type: List[Type[OptimizerRule]]


@SitesRegistry.register_settings
class FANDUELSingleGameFOOTBALLSettings(FANDUELSingleGameSettings):
    sport = Sport.FOOTBALL
    extra_rules = [FANDUELSingleGameMVPRule, FANDUELSingleGameMaxQBRule]
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
class FANDUELSingleGameBasketballSettings(FANDUELSingleGameSettings):
    sport = Sport.BASKETBALL
    extra_rules = [FANDUELSingleGameBasketballRule]
    positions = [
        LineupPosition('MVP', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('STAR', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('PRO', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('FLEX', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('FLEX', ('PG', 'SG', 'SF', 'PF', 'C')),
    ]

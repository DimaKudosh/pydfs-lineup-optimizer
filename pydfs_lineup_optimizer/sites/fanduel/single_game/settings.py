from typing import List, Type
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.rules import OptimizerRule, FanduelSingleGameMVPRule, FanduelSingleGameMaxQBRule, \
    FanduelSingleGameBasketballRule


class FanDuelSingleGameSettings(BaseSettings):
    site = Site.FANDUEL_SINGLE_GAME
    budget = 60000
    max_from_one_team = 4
    extra_rules = [FanduelSingleGameMVPRule]  # type: List[Type[OptimizerRule]]


@SitesRegistry.register_settings
class FanDuelSingleGameFootballSettings(FanDuelSingleGameSettings):
    sport = Sport.FOOTBALL
    extra_rules = [FanduelSingleGameMVPRule, FanduelSingleGameMaxQBRule]
    positions = [
        LineupPosition('MVP', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameBasketballSettings(FanDuelSingleGameSettings):
    sport = Sport.BASKETBALL
    extra_rules = [FanduelSingleGameBasketballRule]
    positions = [
        LineupPosition('MVP', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('STAR', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('PRO', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('FLEX', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('FLEX', ('PG', 'SG', 'SF', 'PF', 'C')),
    ]

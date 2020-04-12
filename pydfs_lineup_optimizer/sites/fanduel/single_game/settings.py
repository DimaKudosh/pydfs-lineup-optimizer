from typing import List, Type
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site, PlayerRank
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.rules import OptimizerRule, FanduelSingleGameMVPRule, FanduelSingleGameMaxQBRule, \
    FanduelSingleGameStarRule, FanduelSingleGameProRule
from pydfs_lineup_optimizer.sites.fanduel.classic.importer import FanDuelCSVImporter, FanDuelMVPCSVImporter
from pydfs_lineup_optimizer.sites.fanduel.single_game.importer import build_fanduel_single_game_importer


class FanDuelSingleGameSettings(BaseSettings):
    site = Site.FANDUEL_SINGLE_GAME
    budget = 60000
    max_from_one_team = 4
    extra_rules = [FanduelSingleGameMVPRule]  # type: List[Type[OptimizerRule]]
    csv_importer = FanDuelMVPCSVImporter  # type: Type[FanDuelCSVImporter]


@SitesRegistry.register_settings
class FanDuelSingleGameFootballSettings(FanDuelSingleGameSettings):
    sport = Sport.FOOTBALL
    extra_rules = [FanduelSingleGameMVPRule, FanduelSingleGameMaxQBRule]
    positions = [
        LineupPosition('MVP', ('QB', 'WR', 'RB', 'TE', 'K'), for_rank=PlayerRank.MVP),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('FLEX', ('QB', 'WR', 'RB', 'TE', 'K')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameBasketballSettings(FanDuelSingleGameSettings):
    sport = Sport.BASKETBALL
    csv_importer = build_fanduel_single_game_importer(mvp=True, star=True, pro=True)
    extra_rules = [FanduelSingleGameMVPRule, FanduelSingleGameStarRule, FanduelSingleGameProRule]
    positions = [
        LineupPosition('MVP', ('PG', 'SG', 'SF', 'PF', 'C'), for_rank=PlayerRank.MVP),
        LineupPosition('STAR', ('PG', 'SG', 'SF', 'PF', 'C'), for_rank=PlayerRank.STAR),
        LineupPosition('PRO', ('PG', 'SG', 'SF', 'PF', 'C'), for_rank=PlayerRank.PRO),
        LineupPosition('FLEX', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('FLEX', ('PG', 'SG', 'SF', 'PF', 'C')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameLOLSettings(FanDuelSingleGameSettings):
    sport = Sport.LEAGUE_OF_LEGENDS
    csv_importer = build_fanduel_single_game_importer(mvp=True, star=True, pro=False)
    extra_rules = [FanduelSingleGameMVPRule, FanduelSingleGameStarRule]
    positions = [
        LineupPosition('MVP', ('TOP', 'MID', 'ADC', 'JNG', 'SUP'), for_rank=PlayerRank.MVP),
        LineupPosition('STAR', ('TOP', 'MID', 'ADC', 'JNG', 'SUP'), for_rank=PlayerRank.STAR),
        LineupPosition('UTIL', ('TOP', 'MID', 'ADC', 'JNG', 'SUP')),
        LineupPosition('UTIL', ('TOP', 'MID', 'ADC', 'JNG', 'SUP')),
        LineupPosition('UTIL', ('TOP', 'MID', 'ADC', 'JNG', 'SUP')),
    ]

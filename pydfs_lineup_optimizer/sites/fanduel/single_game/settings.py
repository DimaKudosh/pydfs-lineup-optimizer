from typing import Type
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.rules import FanduelSingleGameMaxQBRule
from pydfs_lineup_optimizer.sites.fanduel.classic.importer import FanDuelCSVImporter, FanDuelMVPCSVImporter
from pydfs_lineup_optimizer.sites.fanduel.single_game.importer import build_fanduel_single_game_importer, \
    FanDuelSingleGameHockeyCSVImporter
from pydfs_lineup_optimizer.lineup_exporter import FanDuelCSVLineupExporter


class FanDuelSingleGameSettings(BaseSettings):
    site = Site.FANDUEL_SINGLE_GAME
    budget = 60000
    max_from_one_team = 4
    csv_importer = FanDuelMVPCSVImporter  # type: Type[FanDuelCSVImporter]
    csv_exporter = FanDuelCSVLineupExporter


@SitesRegistry.register_settings
class FanDuelSingleGameFootballSettings(FanDuelSingleGameSettings):
    sport = Sport.FOOTBALL
    extra_rules = [FanduelSingleGameMaxQBRule]
    positions = [
        LineupPosition('MVP', ('MVP', )),
        LineupPosition('UTIL', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('UTIL', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('UTIL', ('QB', 'WR', 'RB', 'TE', 'K')),
        LineupPosition('UTIL', ('QB', 'WR', 'RB', 'TE', 'K')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameBasketballSettings(FanDuelSingleGameSettings):
    sport = Sport.BASKETBALL
    csv_importer = build_fanduel_single_game_importer(mvp=True, star=True, pro=True)
    positions = [
        LineupPosition('MVP', ('MVP', )),
        LineupPosition('STAR', ('STAR', )),
        LineupPosition('PRO', ('PRO', )),
        LineupPosition('UTIL', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('UTIL', ('PG', 'SG', 'SF', 'PF', 'C')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameLOLSettings(FanDuelSingleGameSettings):
    sport = Sport.LEAGUE_OF_LEGENDS
    csv_importer = build_fanduel_single_game_importer(mvp=True, star=True, pro=False)
    positions = [
        LineupPosition('MVP', ('MVP', )),
        LineupPosition('STAR', ('STAR', )),
        LineupPosition('UTIL', ('TOP', 'MID', 'ADC', 'JNG', 'SUP')),
        LineupPosition('UTIL', ('TOP', 'MID', 'ADC', 'JNG', 'SUP')),
        LineupPosition('UTIL', ('TOP', 'MID', 'ADC', 'JNG', 'SUP')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameBaseballSettings(FanDuelSingleGameSettings):
    sport = Sport.BASEBALL
    csv_importer = build_fanduel_single_game_importer(mvp=True, star=True, pro=False)
    positions = [
        LineupPosition('MVP', ('MVP', )),
        LineupPosition('STAR', ('STAR', )),
        LineupPosition('UTIL', ('1B', '2B', '3B', 'SS', 'OF', 'C')),
        LineupPosition('UTIL', ('1B', '2B', '3B', 'SS', 'OF', 'C')),
        LineupPosition('UTIL', ('1B', '2B', '3B', 'SS', 'OF', 'C')),
    ]


@SitesRegistry.register_settings
class FanDuelSingleGameHockeySettings(FanDuelSingleGameSettings):
    sport = Sport.HOCKEY
    csv_importer = FanDuelSingleGameHockeyCSVImporter
    positions = [
        LineupPosition('CAPTAIN', ('CAPTAIN', )),
        LineupPosition('UTIL', ('C', 'W', 'D')),
        LineupPosition('UTIL', ('C', 'W', 'D')),
        LineupPosition('UTIL', ('C', 'W', 'D')),
        LineupPosition('UTIL', ('C', 'W', 'D')),
    ]

from typing import List, Type, Optional
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site, PlayerRank
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import IndividualSportLineupPrinter
from pydfs_lineup_optimizer.rules import OptimizerRule, FanduelBaseballRosterRule, FanduelSingleGameStarRule
from pydfs_lineup_optimizer.sites.fanduel.classic.importer import FanDuelCSVImporter
from pydfs_lineup_optimizer.sites.fanduel.single_game.importer import build_fanduel_single_game_importer


class FanDuelSettings(BaseSettings):
    site = Site.FANDUEL
    budget = 60000
    max_from_one_team = 4  # type: Optional[int]
    min_teams = 3  # type: Optional[int]
    csv_importer = FanDuelCSVImporter


@SitesRegistry.register_settings
class FanDuelBasketballSettings(FanDuelSettings):
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
        LineupPosition('FLEX', ('RB', 'WR', 'TE')),
        LineupPosition('DEF', ('D', )),
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
    extra_rules = [FanduelBaseballRosterRule]
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
class FanDuelGolfSettings(FanDuelSettings):
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


@SitesRegistry.register_settings
class FanDuelLOLSettings(FanDuelSettings):
    sport = Sport.LEAGUE_OF_LEGENDS
    max_from_one_team = 4
    min_teams = 3
    csv_importer = build_fanduel_single_game_importer(mvp=False, star=True, pro=False)
    extra_rules = [FanduelSingleGameStarRule]  # type: List[Type[OptimizerRule]]
    positions = [
        LineupPosition('STAR', ('TOP', 'MID', 'ADC', 'JNG', 'SUP'), for_rank=PlayerRank.STAR),
        LineupPosition('TOP', ('TOP',)),
        LineupPosition('JNG', ('JNG',)),
        LineupPosition('MID', ('MID',)),
        LineupPosition('ADC', ('ADC',)),
        LineupPosition('SUP', ('SUP',)),
        LineupPosition('TEAM', ('TEAM',)),
    ]

from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import IndividualSportLineupPrinter
from typing import Optional


class FantasyDraftSettings(BaseSettings):
    site = Site.FANTASY_DRAFT
    budget = 100000
    max_from_one_team = 6  # type: Optional[int]


@SitesRegistry.register_settings
class FantasyDraftBasketballSettings(FantasyDraftSettings):
    sport = Sport.BASKETBALL
    positions = [
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('F/C', ('SF', 'PF', 'C')),
        LineupPosition('F/C', ('SF', 'PF', 'C')),
        LineupPosition('F/C', ('SF', 'PF', 'C')),
        LineupPosition('UTIL', ('PG', 'SG', 'SF', 'PF', 'C')),
        LineupPosition('UTIL', ('PG', 'SG', 'SF', 'PF', 'C')),
    ]


@SitesRegistry.register_settings
class FantasyDraftFootballSettings(FantasyDraftSettings):
    sport = Sport.FOOTBALL
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('TE', ('TE', )),
        LineupPosition('FLEX', ('RB', 'WR', 'TE')),
        LineupPosition('FLEX', ('RB', 'WR', 'TE')),
        LineupPosition('DST', ('DST', ))
    ]


@SitesRegistry.register_settings
class FantasyDraftHockeySettings(FantasyDraftSettings):
    sport = Sport.HOCKEY
    positions = [
        LineupPosition('C', ('C', )),
        LineupPosition('C', ('C', )),
        LineupPosition('W', ('W', )),
        LineupPosition('W', ('W', )),
        LineupPosition('D', ('D', )),
        LineupPosition('UTIL', ('C', 'W', 'D')),
        LineupPosition('UTIL', ('C', 'W', 'D')),
        LineupPosition('Team G', ('TG', )),
    ]


@SitesRegistry.register_settings
class FantasyDraftBaseballSettings(FantasyDraftSettings):
    sport = Sport.BASEBALL
    positions = [
        LineupPosition('P', ('P', )),
        LineupPosition('P', ('P', )),
        LineupPosition('IF', ('1B', '2B', '3B', 'SS', 'IF', 'C',)),
        LineupPosition('IF', ('1B', '2B', '3B', 'SS', 'IF', 'C',)),
        LineupPosition('IF', ('1B', '2B', '3B', 'SS', 'IF', 'C',)),
        LineupPosition('OF', ('LF', 'CF', 'RF', 'OF')),
        LineupPosition('OF', ('LF', 'CF', 'RF', 'OF')),
        LineupPosition('OF', ('LF', 'CF', 'RF', 'OF')),
        LineupPosition('UTIL', ('1B', '2B', '3B', 'SS', 'IF', 'C', 'LF', 'CF', 'RF', 'OF')),
        LineupPosition('UTIL', ('1B', '2B', '3B', 'SS', 'IF', 'C', 'LF', 'CF', 'RF', 'OF')),
    ]


@SitesRegistry.register_settings
class FantasyDraftGolfSettings(FantasyDraftSettings):
    sport = Sport.GOLF
    max_from_one_team = None
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
    ]

from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import IndividualSportLineupPrinter


class DraftKingsSettings(BaseSettings):
    site = Site.DRAFTKINGS
    budget = 50000


@SitesRegistry.register_settings
class DraftKingsBasketballSettings(DraftKingsSettings):
    sport = Sport.BASKETBALL
    positions = [
        LineupPosition('PG', ('PG', )),
        LineupPosition('SG', ('SG', )),
        LineupPosition('SF', ('SF', )),
        LineupPosition('PF', ('PF', )),
        LineupPosition('C', ('C', )),
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('F', ('SF', 'PF')),
        LineupPosition('UTIL', ('PG', 'SG', 'PF', 'SF', 'C'))
    ]


@SitesRegistry.register_settings
class DraftKingsFootballSettings(DraftKingsSettings):
    sport = Sport.FOOTBALL
    positions = [
        LineupPosition('QB', ('QB',)),
        LineupPosition('WR1', ('WR',)),
        LineupPosition('WR2', ('WR',)),
        LineupPosition('WR3', ('WR',)),
        LineupPosition('RB1', ('RB',)),
        LineupPosition('RB2', ('RB',)),
        LineupPosition('TE', ('TE',)),
        LineupPosition('FLEX', ('WR', 'RB', 'TE')),
        LineupPosition('DST', ('DST',))
    ]


@SitesRegistry.register_settings
class DraftKingsHockeySettings(DraftKingsSettings):
    sport = Sport.HOCKEY
    positions = [
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('C', ('C',)),
        LineupPosition('C', ('C',)),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('G', ('G',)),
        LineupPosition('UTIL', ('LW', 'RW', 'C', 'D'))
    ]


@SitesRegistry.register_settings
class DraftKingsBaseballSettings(DraftKingsSettings):
    sport = Sport.BASEBALL
    max_from_one_team = 5
    positions = [
        LineupPosition('P', ('SP', 'RP')),
        LineupPosition('P', ('SP', 'RP')),
        LineupPosition('C', ('C', )),
        LineupPosition('1B', ('1B', )),
        LineupPosition('2B', ('2B', )),
        LineupPosition('3B', ('3B', )),
        LineupPosition('SS', ('SS', )),
        LineupPosition('OF', ('OF', )),
        LineupPosition('OF', ('OF', )),
        LineupPosition('OF', ('OF', )),
    ]


@SitesRegistry.register_settings
class DraftKingsGolfSettings(DraftKingsSettings):
    sport = Sport.GOLF
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
    ]


@SitesRegistry.register_settings
class DraftKingsSoccerSettings(DraftKingsSettings):
    sport = Sport.SOCCER
    positions = [
        LineupPosition('GK', ('GK', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('M', ('M', )),
        LineupPosition('M', ('M', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('UTIL', ('D', 'M', 'F', )),
    ]


@SitesRegistry.register_settings
class DraftKingsCanadianFootballSettings(DraftKingsSettings):
    sport = Sport.CANADIAN_FOOTBALL
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('DST', ('DST', )),
    ]


@SitesRegistry.register_settings
class DraftKingsMMA(DraftKingsSettings):
    sport = Sport.MMA
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
    ]

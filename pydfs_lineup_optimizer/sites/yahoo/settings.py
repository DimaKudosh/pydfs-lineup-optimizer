from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry


class YahooSettings(BaseSettings):
    site = Site.YAHOO
    budget = 200
    max_from_one_team = 6


@SitesRegistry.register_settings
class YahooBasketballSettings(YahooSettings):
    sport = Sport.BASKETBALL
    positions = [
        LineupPosition('PG', ('PG', )),
        LineupPosition('SG', ('SG', )),
        LineupPosition('SF', ('SF', )),
        LineupPosition('PF', ('PF', )),
        LineupPosition('C', ('C', )),
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('F', ('SF', 'PF')),
        LineupPosition('UTIL', ('PG', 'SG', 'SF', 'PF', 'C'))
    ]


@SitesRegistry.register_settings
class YahooFootballSettings(YahooSettings):
    sport = Sport.FOOTBALL
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('TE', ('TE', )),
        LineupPosition('FLEX', ('WR', 'RB', 'TE')),
        LineupPosition('DEF', ('DEF', ))
    ]


@SitesRegistry.register_settings
class YahooHockeySettings(YahooSettings):
    sport = Sport.HOCKEY
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('C', ('C', )),
        LineupPosition('C', ('C', )),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('D', ('D', ))
    ]


@SitesRegistry.register_settings
class YahooBaseballSettings(YahooSettings):
    sport = Sport.BASEBALL
    positions = [
        LineupPosition('P', ('P',)),
        LineupPosition('P', ('P',)),
        LineupPosition('C', ('C',)),
        LineupPosition('1B', ('1B',)),
        LineupPosition('2B', ('2B',)),
        LineupPosition('3B', ('3B',)),
        LineupPosition('SS', ('SS',)),
        LineupPosition('OF', ('OF',)),
        LineupPosition('OF', ('OF',)),
        LineupPosition('OF', ('OF',)),
    ]


@SitesRegistry.register_settings
class YahooGolfSettings(YahooSettings):
    sport = Sport.GOLF
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
    ]


@SitesRegistry.register_settings
class YahooSoccerSettings(YahooSettings):
    sport = Sport.SOCCER
    positions = [
        LineupPosition('GK', ('GK', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('M', ('M', )),
        LineupPosition('M', ('M', )),
        LineupPosition('M', ('M', )),
        LineupPosition('M', ('M', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('UTIL', ('D', 'M', 'F')),
    ]

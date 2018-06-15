from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport


class YahooSettings(BaseSettings):
    budget = 200
    max_from_one_team = 6


class YahooBasketballSettings(YahooSettings):
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


class YahooFootballSettings(YahooSettings):
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


class YahooHockeySettings(YahooSettings):
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


class YahooBaseballSettings(YahooSettings):
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


class YahooGolfSettings(YahooSettings):
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
    ]


class YahooSoccerSettings(YahooSettings):
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


YAHOO_SETTINGS_MAPPING = {
    Sport.BASKETBALL: YahooBasketballSettings,
    Sport.FOOTBALL: YahooFootballSettings,
    Sport.HOCKEY: YahooHockeySettings,
    Sport.BASEBALL: YahooBaseballSettings,
    Sport.GOLF: YahooGolfSettings,
    Sport.SOCCER: YahooSoccerSettings,
}

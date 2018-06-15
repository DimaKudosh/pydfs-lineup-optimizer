from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport


class FanDuelSettings(BaseSettings):
    budget = 60000
    max_from_one_team = 4


class FanDuelBasketballSettings(FanDuelSettings):
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


class FanDuelFootballSettings(FanDuelSettings):
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('TE', ('TE', )),
        LineupPosition('D', ('D', )),
        LineupPosition('K', ('K', )),
    ]


class FanDuelHockeySettings(FanDuelSettings):
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


class FanDuelBaseballSettings(FanDuelSettings):
    budget = 35000
    positions = [
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


class FanDuelWnbaSettings(FanDuelSettings):
    budget = 40000
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
    ]


FANDUEL_SETTINGS_MAPPING = {
    Sport.BASKETBALL: FanDuelBasketballSettings,
    Sport.FOOTBALL: FanDuelFootballSettings,
    Sport.HOCKEY: FanDuelHockeySettings,
    Sport.BASEBALL: FanDuelBaseballSettings,
    Sport.WNBA: FanDuelWnbaSettings,
}

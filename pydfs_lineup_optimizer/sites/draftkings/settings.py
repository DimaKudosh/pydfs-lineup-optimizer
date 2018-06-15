from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport


class DraftKingsSettings(BaseSettings):
    budget = 50000


class DraftKingsBasketballSettings(DraftKingsSettings):
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


class DraftKingsFootballSettings(DraftKingsSettings):
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


class DraftKingsHockeySettings(DraftKingsSettings):
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


class DraftKingsBaseballSettings(DraftKingsSettings):
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


class DraftKingsGolfSettings(DraftKingsSettings):
    positions = [
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
    ]


class DraftKingsSoccerSettings(DraftKingsSettings):
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


class DraftKingsCanadianFootballSettings(DraftKingsSettings):
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('DST', ('DST', )),
    ]


class DraftKingsLOLSettings(DraftKingsSettings):
    positions = [
        LineupPosition('TOP', ('TOP', )),
        LineupPosition('JNG', ('JNG', )),
        LineupPosition('MID', ('MID', )),
        LineupPosition('ADC', ('ADC', )),
        LineupPosition('SUP', ('SUP', )),
        LineupPosition('FLEX', ('TOP', 'JNG', 'MID', 'ADC', 'SUP', )),
        LineupPosition('FLEX', ('TOP', 'JNG', 'MID', 'ADC', 'SUP', )),
        LineupPosition('TEAM', ('TEAM', )),
    ]


DRAFTKINGS_SETTINGS_MAPPING = {
    Sport.BASKETBALL: DraftKingsBasketballSettings,
    Sport.FOOTBALL: DraftKingsFootballSettings,
    Sport.HOCKEY: DraftKingsHockeySettings,
    Sport.BASEBALL: DraftKingsBaseballSettings,
    Sport.GOLF: DraftKingsGolfSettings,
    Sport.SOCCER: DraftKingsSoccerSettings,
    Sport.CANADIAN_FOOTBALL: DraftKingsCanadianFootballSettings,
    Sport.LEAGUE_OF_LEGENDS: DraftKingsLOLSettings,
}

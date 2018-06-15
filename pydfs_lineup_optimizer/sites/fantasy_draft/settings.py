from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport


class FantasyDraftSettings(BaseSettings):
    budget = 100000
    max_from_one_team = 6


class FantasyDraftBasketballSettings(FantasyDraftSettings):
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


class FantasyDraftFootballSettings(FantasyDraftSettings):
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


class FantasyDraftHockeySettings(FantasyDraftSettings):
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


class FantasyDraftBaseballSettings(FantasyDraftSettings):
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


class FantasyDraftGolfSettings(FantasyDraftSettings):
    positions = [
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
        LineupPosition('G', ('G', )),
    ]


FANTASY_DRAFT_SETTINGS_MAPPING = {
    Sport.BASKETBALL: FantasyDraftBasketballSettings,
    Sport.FOOTBALL: FantasyDraftFootballSettings,
    Sport.HOCKEY: FantasyDraftHockeySettings,
    Sport.BASEBALL: FantasyDraftBaseballSettings,
    Sport.GOLF: FantasyDraftGolfSettings,
}

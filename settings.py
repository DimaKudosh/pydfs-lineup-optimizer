from abc import ABCMeta


class BaseSettings:
    __metaclass__ = ABCMeta
    budget = 0
    total_players = 0
    positions = {}


class YahooDailyFantasyBasketballSettings(BaseSettings):
    budget = 200
    total_players = 8
    positions = {
        ('PG', ): 1,
        ('SG', ): 1,
        ('SF', ): 1,
        ('PF', ): 1,
        ('C', ): 1,
        ('PG', 'SG'): 3,
        ('PF', 'SF'): 3,
    }


class YahooDailyFantasyFootballSettings(BaseSettings):
    budget = 200
    total_players = 9
    positions = {
        ('QB', ): 1,
        ('WR', ): 3,
        ('RB', ): 2,
        ('TE', ): 1,
        ('WR', 'RB', 'TE'): 7,
        ('DEF', ): 1,
    }


class YahooDailyFantasyHockeySettings(BaseSettings):
    budget = 200
    total_players = 9
    positions = {
        ('G', ): 2,
        ('C', ): 2,
        ('LW', 'RW'): 3,
        ('D', ): 2,
    }


class FanamentsDailyFantasyBasketballSettings(BaseSettings):
    budget = 100
    total_players = 9
    positions = {
        ('PG', ): 1,
        ('SG', ): 1,
        ('SF', ): 1,
        ('PF', ): 1,
        ('C', ): 1,
        ('PG', 'SG'): 3,
        ('PF', 'SF'): 3,
    }

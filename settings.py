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

"""
Store classes with settings for specified daily fantasy sports site and kind of sport.
"""
from abc import ABCMeta, abstractmethod
import csv
from player import Player


class BaseSettings(object):
    __metaclass__ = ABCMeta
    budget = 0
    total_players = 0
    positions = {}

    @abstractmethod
    def load_players_from_CSV(self, filename):
        return NotImplemented


class YahooSettings(BaseSettings):
    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                player = Player(
                    row["Id"],
                    row["First Name"],
                    row["Last Name"],
                    row["Position"],
                    row["Team"],
                    row["Opponent"],
                    float(row["Salary"]),
                    float(row["FPPG"]),
                    True if row["Injury Status"].strip() else False
                )
                players.append(player)
        return players


class YahooDailyFantasyBasketballSettings(YahooSettings):
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


class YahooDailyFantasyFootballSettings(YahooSettings):
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


class YahooDailyFantasyHockeySettings(YahooSettings):
    budget = 200
    total_players = 9
    positions = {
        ('G', ): 2,
        ('C', ): 2,
        ('LW', 'RW'): 3,
        ('D', ): 2,
    }

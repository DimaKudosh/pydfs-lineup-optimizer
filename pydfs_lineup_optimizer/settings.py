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
    no_position_players = 0
    positions = {}

    @abstractmethod
    def load_players_from_CSV(self, filename):
        return NotImplemented


# YAHOO


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
                    row["Position"].split('/'),
                    row["Team"],
                    float(row["Salary"]),
                    float(row["FPPG"]),
                    True if row["Injury Status"].strip() else False
                )
                players.append(player)
        return players


class YahooBasketballSettings(YahooSettings):
    budget = 200
    total_players = 8
    no_position_players = 1
    positions = {
        ('PG', ): 1,
        ('SG', ): 1,
        ('SF', ): 1,
        ('PF', ): 1,
        ('C', ): 1,
        ('PG', 'SG'): 3,
        ('PF', 'SF'): 3,
    }


class YahooFootballSettings(YahooSettings):
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


class YahooHockeySettings(YahooSettings):
    budget = 200
    total_players = 9
    positions = {
        ('G', ): 2,
        ('C', ): 2,
        ('LW', 'RW'): 3,
        ('D', ): 2,
    }


# FanDuel


class FanDuelSettings(BaseSettings):
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
                    row["Position"].split('/'),
                    row["Team"],
                    float(row["Salary"]),
                    float(row["FPPG"]),
                    True if row["Injury Indicator"].strip() else False
                )
                players.append(player)
        return players



class FanDuelBasketballSettings(FanDuelSettings):
    budget = 60000
    total_players = 9
    positions = {
        ('PG', ): 2,
        ('SG', ): 2,
        ('SF', ): 2,
        ('PF', ): 2,
        ('C', ): 1
    }


class FanDuelFootballSettings(FanDuelSettings):
    budget = 60000
    total_players = 9
    positions = {
        ('QB', ): 1,
        ('RB', ): 2,
        ('WR', ): 3,
        ('TE', ): 1,
        ('D', ): 1,
        ('K', ): 1
    }


# DraftKings


class DraftKingsSettings(BaseSettings):
    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                name = row["Name"].split()
                player = Player(
                    '',
                    name[0],
                    name[1] if len(name) > 1 else '',
                    row["Position"].split('/'),
                    row["teamAbbrev"],
                    float(row["Salary"]),
                    float(row["AvgPointsPerGame"])
                )
                players.append(player)
        return players


class DraftKingsBasketballSettings(DraftKingsSettings):
    budget = 50000
    total_players = 8
    no_position_players = 1
    positions = {
        ('PG', ): 1,
        ('SG', ): 1,
        ('SF', ): 1,
        ('PF',): 1,
        ('C', ): 1,
        ('PG', 'SG'): 3,
        ('SF', 'PF'): 3
    }


class DraftKingsFootballSettings(DraftKingsSettings):
    budget = 50000
    total_players = 9
    positions = {
        ('QB', ): 1,
        ('RB', ): 2,
        ('WR', ): 3,
        ('TE', ): 1,
        ('RB', 'WR', 'TE'): 7,
        ('DST', ): 1
    }

# FantasyDraft


class FantasyDraftSettings(BaseSettings):
    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                name = row["Name"].split()
                player = Player(
                    "",
                    name[0],
                    name[1] if len(name) > 1 else '',
                    row["Position"].split('/'),
                    row["Team"],
                    float(row["Salary"].replace('$', '').replace(',', '')),
                    float(row["Avg FPPG"])
                )
                players.append(player)
        return players


class FantasyDraftBasketballSettings(FantasyDraftSettings):
    budget = 100000
    total_players = 8
    no_position_players = 2
    positions = {
        ('PG', 'SG'): 3,
        ('PF', 'SF', 'C'): 3,
    }


class FantasyDraftFootballSettings(FantasyDraftSettings):
    budget = 100000
    total_players = 9
    no_position_players = 0
    positions = {
        ('QB', ): 1,
        ('RB', ): 2,
        ('WR', ): 2,
        ('TE', ): 1,
        ('RB', 'WR', 'TE'): 7,
        ('DST', ): 1
    }


class FantasyDraftHockeySettings(FantasyDraftSettings):
    budget = 100000
    total_players = 8
    no_position_players = 0
    positions = {
        ('C', ): 2,
        ('W', ): 2,
        ('D', ): 1,
        ('C', 'W', 'D'): 7,
        ('TG', ): 1,
    }

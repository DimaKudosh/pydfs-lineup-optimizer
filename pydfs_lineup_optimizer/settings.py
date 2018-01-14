"""
Store classes with settings for specified daily fantasy sports site and kind of sport.
"""
from abc import ABCMeta, abstractmethod
from collections import namedtuple
import csv
from .player import Player


LineupPosition = namedtuple('LineupPosition', ['name', 'positions'])


class BaseSettings(object):
    __metaclass__ = ABCMeta
    budget = 0
    positions = []
    max_from_one_team = None

    @classmethod
    @abstractmethod
    def get_total_players(cls):
        return len(cls.positions)

    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):
        return NotImplemented


# YAHOO


class YahooSettings(BaseSettings):
    max_from_one_team = 6

    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):  # pragma: no cover
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                max_exposure = row.get('Max Exposure')
                player = Player(
                    row['Id'],
                    row['First Name'],
                    row['Last Name'],
                    row['Position'].split('/'),
                    row['Team'],
                    float(row['Salary']),
                    float(row['FPPG']),
                    True if row['Injury Status'].strip() else False,
                    max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None
                )
                players.append(player)
        return players


class YahooBasketballSettings(YahooSettings):
    budget = 200
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
    budget = 200
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
    budget = 200
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
    budget = 200
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


# FanDuel


class FanDuelSettings(BaseSettings):
    max_from_one_team = 4

    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):  # pragma: no cover
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                max_exposure = row.get('Max Exposure')
                player = Player(
                    row['Id'],
                    row['First Name'],
                    row['Last Name'],
                    row['Position'].split('/'),
                    row['Team'],
                    float(row['Salary']),
                    float(row['FPPG']),
                    True if row['Injury Indicator'].strip() else False,
                    max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None
                )
                players.append(player)
        return players



class FanDuelBasketballSettings(FanDuelSettings):
    budget = 60000
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
    budget = 60000
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


# DraftKings


class DraftKingsSettings(BaseSettings):  # pragma: no cover
    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                max_exposure = row.get('Max Exposure')
                name = row['Name'].split()
                player = Player(
                    '',
                    name[0],
                    name[1] if len(name) > 1 else '',
                    row['Position'].split('/'),
                    row['teamAbbrev'],
                    float(row['Salary']),
                    float(row['AvgPointsPerGame']),
                    max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None
                )
                players.append(player)
        return players


class DraftKingsBasketballSettings(DraftKingsSettings):
    budget = 50000
    total_players = 8
    no_position_players = 1
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
    budget = 50000
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
    budget = 50000
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
    budget = 50000
    positions = [
        LineupPosition('P', ('P', )),
        LineupPosition('P', ('P', )),
        LineupPosition('C', ('C', )),
        LineupPosition('1B', ('1B', )),
        LineupPosition('2B', ('2B', )),
        LineupPosition('3B', ('3B', )),
        LineupPosition('SS', ('SS', )),
        LineupPosition('OF', ('OF', )),
        LineupPosition('OF', ('OF', )),
        LineupPosition('OF', ('OF', )),
    ]
    max_from_one_team = 5


# FantasyDraft


class FantasyDraftSettings(BaseSettings):
    max_from_one_team = 6

    @classmethod
    @abstractmethod
    def load_players_from_CSV(cls, filename):  # pragma: no cover
        players = []
        with open(filename, 'r') as csvfile:
            csvdata = csv.DictReader(csvfile, skipinitialspace=True)
            for row in csvdata:
                name = row['Name'].split()
                max_exposure = row.get('Max Exposure')
                player = Player(
                    '',
                    name[0],
                    name[1] if len(name) > 1 else '',
                    row['Position'].split('/'),
                    row['Team'],
                    float(row['Salary'].replace('$', '').replace(',', '')),
                    float(row['Avg FPPG']),
                    max_exposure=float(max_exposure.replace('%', '')) if max_exposure else None
                )
                players.append(player)
        return players


class FantasyDraftBasketballSettings(FantasyDraftSettings):
    budget = 100000
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
    budget = 100000
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
    budget = 100000
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

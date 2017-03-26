from enum import Enum


class Site(Enum):
    DRAFTKINGS = 'DRAFTKINGS'
    FANDUEL = 'FANDUEL'
    YAHOO = 'YAHOO'
    FANTASY_DRAFT = 'FANTASY_DRAFT'


class Sport(Enum):
    BASKETBALL = 'BASKETBALL'
    FOOTBALL = 'FOOTBALL'
    HOCKEY = 'HOCKEY'
    BASEBALL = 'BASEBALL'

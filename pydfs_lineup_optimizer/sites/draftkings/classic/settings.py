from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import IndividualSportLineupPrinter
from pydfs_lineup_optimizer.sites.draftkings.classic.importer import DraftKingsCSVImporter
from pydfs_lineup_optimizer.sites.draftkings.captain_mode.importer import DraftKingsCaptainModeCSVImporter
from pydfs_lineup_optimizer.rules import DraftKingsBaseballRosterRule


class DraftKingsSettings(BaseSettings):
    site = Site.DRAFTKINGS
    budget = 50000
    csv_importer = DraftKingsCSVImporter


@SitesRegistry.register_settings
class DraftKingsBasketballSettings(DraftKingsSettings):
    sport = Sport.BASKETBALL
    min_games = 2
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


@SitesRegistry.register_settings
class DraftKingsWNBASettings(DraftKingsSettings):
    sport = Sport.WNBA
    min_games = 2
    positions = [
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('G', ('PG', 'SG')),
        LineupPosition('F', ('SF', 'PF')),
        LineupPosition('F', ('SF', 'PF')),
        LineupPosition('F', ('SF', 'PF')),
        LineupPosition('UTIL', ('PG', 'SG', 'PF', 'SF', 'C'))
    ]    


@SitesRegistry.register_settings
class DraftKingsFootballSettings(DraftKingsSettings):
    sport = Sport.FOOTBALL
    min_games = 2
    positions = [
        LineupPosition('QB', ('QB',)),
        LineupPosition('RB', ('RB',)),
        LineupPosition('RB', ('RB',)),
        LineupPosition('WR', ('WR',)),
        LineupPosition('WR', ('WR',)),
        LineupPosition('WR', ('WR',)),
        LineupPosition('TE', ('TE',)),
        LineupPosition('FLEX', ('WR', 'RB', 'TE')),
        LineupPosition('DST', ('DST',))
    ]


@SitesRegistry.register_settings
class DraftKingsHockeySettings(DraftKingsSettings):
    sport = Sport.HOCKEY
    min_teams = 3
    total_teams_exclude_positions = ['G']
    positions = [
        LineupPosition('C', ('C',)),
        LineupPosition('C', ('C',)),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('W', ('LW', 'RW')),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('G', ('G',)),
        LineupPosition('UTIL', ('LW', 'RW', 'C', 'D'))
    ]


@SitesRegistry.register_settings
class DraftKingsBaseballSettings(DraftKingsSettings):
    sport = Sport.BASEBALL
    min_games = 2
    max_from_one_team = None
    extra_rules = [DraftKingsBaseballRosterRule]
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


@SitesRegistry.register_settings
class DraftKingsGolfSettings(DraftKingsSettings):
    sport = Sport.GOLF
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
        LineupPosition('G', ('G',)),
    ]


@SitesRegistry.register_settings
class DraftKingsSoccerSettings(DraftKingsSettings):
    sport = Sport.SOCCER
    min_teams = 3
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


@SitesRegistry.register_settings
class DraftKingsCanadianFootballSettings(DraftKingsSettings):
    sport = Sport.CANADIAN_FOOTBALL
    min_teams = 2
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('DST', ('DST', )),
    ]


@SitesRegistry.register_settings
class DraftKingsCollegeFootballSettings(DraftKingsSettings):
    sport = Sport.CANADIAN_FOOTBALL
    min_games = 2
    positions = [
        LineupPosition('QB', ('QB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('RB', ('RB', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('WR', ('WR', )),
        LineupPosition('FLEX', ('RB', 'WR', )),
        LineupPosition('SUPER FLEX', ('QB', 'RB', 'WR', )),
    ]


@SitesRegistry.register_settings
class DraftKingsMMA(DraftKingsSettings):
    sport = Sport.MMA
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
        LineupPosition('F', ('F', )),
    ]


@SitesRegistry.register_settings
class DraftKingsNascarSettings(DraftKingsSettings):
    sport = Sport.NASCAR
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
        LineupPosition('D', ('D', )),
    ]


@SitesRegistry.register_settings
class DraftKingsTennisSettings(DraftKingsSettings):
    sport = Sport.TENNIS
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('P', ('P',)),
        LineupPosition('P', ('P',)),
        LineupPosition('P', ('P',)),
        LineupPosition('P', ('P',)),
        LineupPosition('P', ('P',)),
        LineupPosition('P', ('P',)),
    ]


@SitesRegistry.register_settings
class DraftKingsCSGOSettings(DraftKingsSettings):
    sport = Sport.CS
    max_from_one_team = 3
    min_games = 2
    csv_importer = DraftKingsCaptainModeCSVImporter
    lineup_printer = IndividualSportLineupPrinter
    positions = [
        LineupPosition('CPT', ('CPT',)),
        LineupPosition('FLEX', ('FLEX',)),
        LineupPosition('FLEX', ('FLEX',)),
        LineupPosition('FLEX', ('FLEX',)),
        LineupPosition('FLEX', ('FLEX',)),
        LineupPosition('FLEX', ('FLEX',)),
    ]

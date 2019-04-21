from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry


class DraftKingsCaptainModeSettings(BaseSettings):
    site = Site.DRAFTKINGS_CAPTAIN_MODE
    budget = 50000
    max_from_one_team = 5


@SitesRegistry.register_settings
class DraftKingsCaptainModeFootballSettings(DraftKingsCaptainModeSettings):
    sport = Sport.FOOTBALL
    positions = [
        LineupPosition('CPT', ('CPT', )),
        LineupPosition('FLEX', ('FLEX', )),
        LineupPosition('FLEX', ('FLEX', )),
        LineupPosition('FLEX', ('FLEX', )),
        LineupPosition('FLEX', ('FLEX', )),
        LineupPosition('FLEX', ('FLEX', )),
    ]


@SitesRegistry.register_settings
class DraftKingsCaptainModeBasketballSettings(DraftKingsCaptainModeSettings):
    sport = Sport.BASKETBALL
    positions = [
        LineupPosition('CPT', ('CPT', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
    ]


@SitesRegistry.register_settings
class DraftKingsLOLSettings(DraftKingsCaptainModeSettings):
    sport = Sport.LEAGUE_OF_LEGENDS
    max_from_one_team = 4
    positions = [
        LineupPosition('CPT', ('CPT', )),
        LineupPosition('TOP', ('TOP', )),
        LineupPosition('JNG', ('JNG', )),
        LineupPosition('MID', ('MID', )),
        LineupPosition('ADC', ('ADC', )),
        LineupPosition('SUP', ('SUP', )),
        LineupPosition('TEAM', ('TEAM', )),
    ]


@SitesRegistry.register_settings
class DraftKingsCaptainModeBaseballSettings(DraftKingsCaptainModeSettings):
    sport = Sport.BASEBALL
    positions = [
        LineupPosition('CPT', ('CPT', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
        LineupPosition('UTIL', ('UTIL', )),
    ]

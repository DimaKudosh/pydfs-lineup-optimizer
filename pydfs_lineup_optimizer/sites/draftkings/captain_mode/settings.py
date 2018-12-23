from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry


class DraftKingsCaptainModeSettings(BaseSettings):
    site = Site.DRAFTKINGS_CAPTAIN_MODE
    budget = 50000


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

from typing import List
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.lineup_printer import DraftKingTiersLineupPrinter
from pydfs_lineup_optimizer.sites.draftkings.tiers.importer import DraftKingsTiersCSVImporter
from pydfs_lineup_optimizer.rules import DraftKingsTiersRule


class DraftKingsTiersSettings(BaseSettings):
    site = Site.DRAFTKINGS_TIERS
    csv_importer = DraftKingsTiersCSVImporter
    min_games = 2
    budget = None
    positions = []  # type: List[LineupPosition]
    extra_rules = [DraftKingsTiersRule]
    lineup_printer = DraftKingTiersLineupPrinter


@SitesRegistry.register_settings
class DraftKingsTiersBasketballSettings(DraftKingsTiersSettings):
    sport = Sport.BASKETBALL


@SitesRegistry.register_settings
class DraftKingsTiersBaseballSettings(DraftKingsTiersSettings):
    sport = Sport.BASEBALL


@SitesRegistry.register_settings
class DraftKingsTiersHockeySettings(DraftKingsTiersSettings):
    sport = Sport.HOCKEY


@SitesRegistry.register_settings
class DraftKingsTiersFootballSettings(DraftKingsTiersSettings):
    sport = Sport.FOOTBALL

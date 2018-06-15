from pydfs_lineup_optimizer.constants import Site
from .draftkings import DRAFTKINGS_SETTINGS_MAPPING, DraftKingsCSVImporter
from .fanduel import FANDUEL_SETTINGS_MAPPING, FanDuelCSVImporter
from .fantasy_draft import FANTASY_DRAFT_SETTINGS_MAPPING, FantasyDraftCSVImporter
from .yahoo import YAHOO_SETTINGS_MAPPING, YahooCSVImporter


SETTINGS_MAPPING = {
    Site.DRAFTKINGS: DRAFTKINGS_SETTINGS_MAPPING,
    Site.FANDUEL: FANDUEL_SETTINGS_MAPPING,
    Site.FANTASY_DRAFT: FANTASY_DRAFT_SETTINGS_MAPPING,
    Site.YAHOO: YAHOO_SETTINGS_MAPPING,
}


CSV_IMPORTERS_MAPPING = {
    Site.DRAFTKINGS: DraftKingsCSVImporter,
    Site.FANDUEL: FanDuelCSVImporter,
    Site.FANTASY_DRAFT: FantasyDraftCSVImporter,
    Site.YAHOO: YahooCSVImporter,
}

__version__ = '1.4.0'

from .player import Player
from .exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName
from .lineup_optimizer import LineupOptimizer
from .lineup import Lineup
from .settings import YahooBasketballSettings, YahooFootballSettings, YahooHockeySettings, YahooBaseballSettings, \
    FanDuelBasketballSettings, FanDuelFootballSettings, FanDuelHockeySettings, FanDuelBaseballSettings, \
    DraftKingsBasketballSettings, DraftKingsFootballSettings, DraftKingsHockeySettings, DraftKingsBaseballSettings, \
    FantasyDraftBasketballSettings, FantasyDraftFootballSettings, FantasyDraftHockeySettings
from .constants import Site, Sport
from .lineup_exporter import CSVLineupExporter


settings_mapping = {
    Site.DRAFTKINGS: {
        Sport.BASKETBALL: DraftKingsBasketballSettings,
        Sport.FOOTBALL: DraftKingsFootballSettings,
        Sport.HOCKEY: DraftKingsHockeySettings,
        Sport.BASEBALL: DraftKingsBaseballSettings,
    },
    Site.FANDUEL: {
        Sport.BASKETBALL: FanDuelBasketballSettings,
        Sport.FOOTBALL: FanDuelFootballSettings,
        Sport.HOCKEY: FanDuelHockeySettings,
        Sport.BASEBALL: FanDuelBaseballSettings,
    },
    Site.YAHOO: {
        Sport.BASKETBALL: YahooBasketballSettings,
        Sport.FOOTBALL: YahooFootballSettings,
        Sport.HOCKEY: YahooHockeySettings,
        Sport.BASEBALL: YahooBaseballSettings,
    },
    Site.FANTASY_DRAFT: {
        Sport.BASKETBALL: FantasyDraftBasketballSettings,
        Sport.FOOTBALL: FantasyDraftFootballSettings,
        Sport.HOCKEY: FantasyDraftHockeySettings,
    },
}


def get_optimizer(site, sport):
    try:
        return LineupOptimizer(settings_mapping[site][sport])
    except KeyError:
        raise NotImplementedError

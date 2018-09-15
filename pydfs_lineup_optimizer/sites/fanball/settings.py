from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.constants import Sport, Site
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry


class FanBallSettings(BaseSettings):
    site = Site.FANBALL
    budget = 55000


@SitesRegistry.register_settings
class FanBallFootballSettings(FanBallSettings):
    sport = Sport.FOOTBALL
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



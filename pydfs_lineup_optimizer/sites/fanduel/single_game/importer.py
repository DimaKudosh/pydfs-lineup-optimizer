from copy import deepcopy
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site
from pydfs_lineup_optimizer.sites.fanduel.classic.importer import FanDuelCSVImporter


@SitesRegistry.register_csv_importer
class FanDuelSingleGameCSVImporter(FanDuelCSVImporter):  # pragma: nocover
    site = Site.FANDUEL_SINGLE_GAME

    def import_players(self):
        players = super(FanDuelSingleGameCSVImporter, self).import_players()
        mvps = []
        for player in players:
            mvp_player = deepcopy(player)
            mvp_player.fppg *= 1.5
            mvp_player.is_mvp = True
            mvps.append(mvp_player)
        players.extend(mvps)
        return players

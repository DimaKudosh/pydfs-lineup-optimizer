from copy import deepcopy
from pydfs_lineup_optimizer.sites.sites_registry import SitesRegistry
from pydfs_lineup_optimizer.constants import Site
from pydfs_lineup_optimizer.sites.fanduel.classic.importer import FanDuelCSVImporter


@SitesRegistry.register_csv_importer
class FanDuelSingleGameCSVImporter(FanDuelCSVImporter):  # pragma: nocover
    site = Site.FANDUEL_SINGLE_GAME

    def import_players(self):
        players = super().import_players()
        mvps = []
        for player in players:
            mvp_player = deepcopy(player)
            mvp_player.fppg *= 1.5
            mvp_player.is_mvp = True
            mvps.append(mvp_player)
        players.extend(mvps)
        return players


@SitesRegistry.register_csv_importer
class FanDuelBasketballSingleGameCSVImporter(FanDuelCSVImporter):  # pragma: nocover
    site = Site.FANDUEL_SINGLE_GAME

    def import_players(self):
        players = super().import_players()
        mvps = []
        stars = []
        pros = []
        for player in players:
            mvp_player = deepcopy(player)
            mvp_player.fppg *= 2
            mvp_player.is_mvp = True
            mvps.append(mvp_player)
            star_player = deepcopy(player)
            star_player.fppg *= 1.5
            star_player.is_star = True
            stars.append(star_player)
            pro_player = deepcopy(player)
            pro_player.fppg *= 1.2
            pro_player.is_pro = True
            pros.append(pro_player)
        players.extend(mvps + stars + pros)
        return players

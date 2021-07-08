from copy import deepcopy
from typing import Type
from pydfs_lineup_optimizer.sites.fanduel.classic.importer import FanDuelCSVImporter


def build_fanduel_single_game_importer(mvp=True, star=False, pro=False) -> Type[FanDuelCSVImporter]:
    class FanDuelSingleGameCSVImporter(FanDuelCSVImporter):  # pragma: nocover
        def import_players(self):
            players = super().import_players()
            extra_players = []
            for player in players:
                if mvp:
                    mvp_player = deepcopy(player)
                    mvp_player.fppg *= 2
                    mvp_player._original_positions = player.positions
                    mvp_player.positions = ('MVP', )
                    extra_players.append(mvp_player)
                if star:
                    star_player = deepcopy(player)
                    star_player.fppg *= 1.5
                    star_player._original_positions = player.positions
                    star_player.positions = ('STAR', )
                    extra_players.append(star_player)
                if pro:
                    pro_player = deepcopy(player)
                    pro_player.fppg *= 1.2
                    pro_player._original_positions = player.positions
                    pro_player.positions = ('PRO', )
                    extra_players.append(pro_player)
            players.extend(extra_players)
            return players
    return FanDuelSingleGameCSVImporter


class FanDuelSingleGameHockeyCSVImporter(FanDuelCSVImporter):  # pragma: nocover
    def import_players(self):
        players = super().import_players()
        extra_players = []
        for player in players:
            captain_player = deepcopy(player)
            captain_player.fppg *= 1.5
            captain_player._original_positions = player.positions
            captain_player.positions = ('CAPTAIN', )
            extra_players.append(captain_player)
        players.extend(extra_players)
        return players

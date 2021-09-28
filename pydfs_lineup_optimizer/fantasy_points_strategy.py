from typing import Dict
from random import getrandbits, uniform
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.lineup import Lineup


class BaseFantasyPointsStrategy:
    def get_player_fantasy_points(self, player: Player) -> float:
        raise NotImplementedError

    def set_previous_lineup(self, lineup: Lineup):
        pass


class StandardFantasyPointsStrategy(BaseFantasyPointsStrategy):
    def get_player_fantasy_points(self, player: Player) -> float:
        return player.fppg

    def set_previous_lineup(self, lineup: Lineup):
        pass


class RandomFantasyPointsStrategy(BaseFantasyPointsStrategy):
    def __init__(self, min_deviation: float = 0.0, max_deviation: float = 0.12):
        self.min_deviation = min_deviation
        self.max_deviation = max_deviation

    def get_player_fantasy_points(self, player: Player) -> float:
        if player.fppg_floor is not None and player.fppg_ceil is not None:
            return uniform(player.fppg_floor, player.fppg_ceil)
        multiplier = uniform(
            player.min_deviation if player.min_deviation is not None else self.min_deviation,
            player.max_deviation if player.max_deviation is not None else self.max_deviation
        )
        return player.fppg * (1 + (-1 if bool(getrandbits(1)) else 1) * multiplier)


class ProgressiveFantasyPointsStrategy(BaseFantasyPointsStrategy):
    def __init__(self, scale: float = 0.01):
        self.scale = scale
        self.player_multipliers = {}  # type: Dict[Player, float]

    def get_player_fantasy_points(self, player: Player) -> float:
        if player not in self.player_multipliers:
            self.player_multipliers[player] = 0
        return player.fppg * (1 + self.player_multipliers[player])

    def set_previous_lineup(self, lineup: Lineup):
        lineup_players = set(lineup)
        for player in self.player_multipliers:
            if player in lineup_players:
                self.player_multipliers[player] = 0
            else:
                scale = player.progressive_scale if player.progressive_scale is not None else self.scale
                self.player_multipliers[player] += scale

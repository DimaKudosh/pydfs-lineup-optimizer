from __future__ import division
from collections import namedtuple
from datetime import datetime
from typing import List, Optional
from pytz import timezone


GameInfo = namedtuple('GameInfo', ['home_team', 'away_team', 'starts_at', 'game_started'])


class Player(object):
    def __init__(self,
                 player_id,  # type: str
                 first_name,  # type: str
                 last_name,  # type: str
                 positions,  # type: List[str]
                 team,  # type: str
                 salary,  # type: float
                 fppg,  # type: float
                 is_injured=False,  # type: bool
                 max_exposure=None,  # type: Optional[float]
                 min_exposure=None,  # type: Optional[float]
                 projected_ownership=None,  # type: Optional[float]
                 game_info=None,  # type: Optional[GameInfo]
                 ):
        # type: (...) -> None
        self.id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.positions = positions
        self.team = team.upper()
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured
        self.game_info = game_info
        self._max_exposure = None  # type: Optional[float]
        self.max_exposure = max_exposure
        self._min_exposure = None  # type: Optional[float]
        self.min_exposure = min_exposure
        self._projected_ownership = None  # type: Optional[float]
        self.projected_ownership = projected_ownership

    def __repr__(self):
        return '%s %s (%s)' % (self.full_name, '/'.join(self.positions), self.team)

    def __hash__(self):
        return hash(self.id)

    @property
    def max_exposure(self):
        # type: () -> Optional[float]
        return self._max_exposure

    @max_exposure.setter
    def max_exposure(self, max_exposure):
        # type: (Optional[float]) -> None
        self._max_exposure = max_exposure / 100 if max_exposure and max_exposure > 1 else max_exposure

    @property
    def min_exposure(self):
        # type: () -> Optional[float]
        return self._min_exposure

    @min_exposure.setter
    def min_exposure(self, min_exposure):
        # type: (Optional[float]) -> None
        self._min_exposure = min_exposure / 100 if min_exposure and min_exposure > 1 else min_exposure

    @property
    def projected_ownership(self):
        # type: () -> Optional[float]
        return self._projected_ownership

    @projected_ownership.setter
    def projected_ownership(self, projected_ownership):
        # type: (Optional[float]) -> None
        self._projected_ownership = projected_ownership / 100 if projected_ownership and projected_ownership > 1 \
            else projected_ownership

    @property
    def full_name(self):
        # type: () -> str
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def efficiency(self):
        # type: () -> float
        return round(self.fppg / self.salary, 6)

    @property
    def is_game_started(self):
        # type: () -> bool
        if self.game_info:
            if self.game_info.game_started:
                return True
            starts_at = self.game_info.starts_at
            if starts_at and datetime.now(starts_at.tzinfo) > starts_at:
                return True
        return False


class LineupPlayer(object):
    __slots__ = ['_player', 'lineup_position']

    def __init__(self, player, lineup_position):
        # type: (Player, str) -> None
        self._player = player
        self.lineup_position = lineup_position

    def __getattr__(self, attr_name):
        return getattr(self._player, attr_name)

    def __eq__(self, other):
        if isinstance(other, Player):
            return self._player == other
        elif isinstance(other, LineupPlayer):
            return self._player == other._player
        return NotImplemented

    def __hash__(self):
        return hash(self._player)

    def __repr__(self):
        return repr(self._player)

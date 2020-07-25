from collections import namedtuple
from datetime import datetime
from pytz import timezone
from typing import List, Optional
from pydfs_lineup_optimizer.utils import process_percents
from pydfs_lineup_optimizer.tz import get_timezone


GameInfo = namedtuple('GameInfo', ['home_team', 'away_team', 'starts_at', 'game_started'])


class Player:
    def __init__(self,
                 player_id: str,
                 first_name: str,
                 last_name: str,
                 positions: List[str],
                 team: str,
                 salary: float,
                 fppg: float,
                 is_injured: bool = False,
                 max_exposure: Optional[float] = None,
                 min_exposure: Optional[float] = None,
                 projected_ownership: Optional[float] = None,
                 game_info: Optional[GameInfo] = None,
                 roster_order: Optional[int] = None,
                 min_deviation: Optional[float] = None,
                 max_deviation: Optional[float] = None,
                 is_confirmed_starter: Optional[bool] = None,
                 fppg_floor: Optional[float] = None,
                 fppg_ceil: Optional[float] = None,
                 original_positions: Optional[List[str]] = None,
                 ):
        self.id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.positions = positions
        self.team = team
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured
        self.game_info = game_info
        self.roster_order = roster_order
        self._min_exposure = None  # type: Optional[float]
        self._max_exposure = None  # type: Optional[float]
        self._min_deviation = None  # type: Optional[float]
        self._max_deviation = None  # type: Optional[float]
        self._projected_ownership = None  # type: Optional[float]
        self.min_exposure = min_exposure
        self.max_exposure = max_exposure
        self.min_deviation = min_deviation
        self.max_deviation = max_deviation
        self.projected_ownership = projected_ownership
        self.is_confirmed_starter = is_confirmed_starter
        self.fppg_floor = fppg_floor
        self.fppg_ceil = fppg_ceil
        self._original_positions = original_positions

    def __repr__(self):
        return '%s %s (%s)' % (self.full_name, '/'.join(self.positions), self.team)

    def __hash__(self):
        return hash(self.id)

    @property
    def max_exposure(self) -> Optional[float]:
        return self._max_exposure

    @max_exposure.setter
    def max_exposure(self, max_exposure: Optional[float]):
        self._max_exposure = process_percents(max_exposure)

    @property
    def min_exposure(self) -> Optional[float]:
        return self._min_exposure

    @min_exposure.setter
    def min_exposure(self, min_exposure: Optional[float]):
        self._min_exposure = process_percents(min_exposure)

    @property
    def min_deviation(self) -> Optional[float]:
        return self._min_deviation

    @min_deviation.setter
    def min_deviation(self, min_deviation: Optional[float]):
        self._min_deviation = process_percents(min_deviation)

    @property
    def max_deviation(self) -> Optional[float]:
        return self._max_deviation

    @max_deviation.setter
    def max_deviation(self, max_deviation: Optional[float]):
        self._max_deviation = process_percents(max_deviation)

    @property
    def projected_ownership(self) -> Optional[float]:
        return self._projected_ownership

    @projected_ownership.setter
    def projected_ownership(self, projected_ownership: Optional[float]):
        self._projected_ownership = process_percents(projected_ownership)

    @property
    def full_name(self) -> str:
        return '{} {}'.format(self.first_name, self.last_name)

    @property
    def efficiency(self) -> float:
        return round(self.fppg / self.salary, 6)

    @property
    def is_game_started(self) -> bool:
        if self.game_info:
            if self.game_info.game_started:
                return True
            starts_at = self.game_info.starts_at
            time_now = datetime.now().replace(tzinfo=timezone(get_timezone()))
            if starts_at and time_now > starts_at:
                return True
        return False

    @property
    def original_positions(self) -> List[str]:
        return self._original_positions or self.positions


class LineupPlayer:
    def __init__(self, player: Player, lineup_position: str, used_fppg: Optional[float] = None):
        self._player = player
        self.lineup_position = lineup_position
        self.used_fppg = used_fppg

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

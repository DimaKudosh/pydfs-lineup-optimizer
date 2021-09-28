from datetime import datetime
from pytz import timezone
from typing import List, Optional, Tuple, Sequence
from pydfs_lineup_optimizer.tz import get_timezone


class GameInfo:
    def __init__(
            self,
            home_team: Optional[str],
            away_team: Optional[str],
            starts_at: Optional[datetime],
            game_started: bool = False
    ):
        self.home_team = home_team
        self.away_team = away_team
        self.starts_at = starts_at
        self.game_started = game_started

    def __hash__(self):
        return hash((self.home_team, self.away_team))


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
                 progressive_scale: Optional[float] = None,
                 original_positions: Optional[List[str]] = None,
                 ):
        self.id = player_id
        self.first_name = first_name
        self.last_name = last_name
        self.positions = positions  # type: ignore
        self.team = team
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured
        self.game_info = game_info
        self.roster_order = roster_order
        self.min_exposure = min_exposure
        self.max_exposure = max_exposure
        self.min_deviation = min_deviation
        self.max_deviation = max_deviation
        self.projected_ownership = projected_ownership
        self.is_confirmed_starter = is_confirmed_starter
        self.fppg_floor = fppg_floor
        self.fppg_ceil = fppg_ceil
        self.progressive_scale = progressive_scale
        self.original_positions = original_positions  # type: ignore

    def __repr__(self):
        return '%s %s (%s)' % (self.full_name, '/'.join(self.positions), self.team)

    def __hash__(self):
        return hash((self.id, self.positions))

    def __eq__(self, other):
        return (self.id, self.positions) == (other.id, other.positions)

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
    def positions(self) -> Tuple[str, ...]:
        return self._positions

    @positions.setter
    def positions(self, value: Sequence[str]):
        self._positions = tuple(sorted(value))

    @property
    def original_positions(self) -> Tuple[str, ...]:
        return self._original_positions or self.positions

    @original_positions.setter
    def original_positions(self, value: Optional[Sequence[str]]):
        self._original_positions = tuple(sorted(value)) if value else None


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

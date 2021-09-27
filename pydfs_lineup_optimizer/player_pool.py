from typing import FrozenSet, List, Optional, Set, Union, Iterable, Dict, DefaultDict
from collections import defaultdict
from itertools import chain
from pydfs_lineup_optimizer.settings import BaseSettings
from pydfs_lineup_optimizer.player import Player, GameInfo
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from pydfs_lineup_optimizer.utils import link_players_with_positions, ratio, list_intersection
from pydfs_lineup_optimizer.settings import LineupPosition


DirtyPlayer = Union[Player, str]


class BaseFilter:
    def filter(self, player: Player, include_not_matched: bool = True) -> bool:
        raise NotImplemented


class PlayerFilter(BaseFilter):
    def __init__(
            self,
            from_value: float = 0,
            to_value: Optional[float] = None,
            positions: Optional[Iterable[str]] = None,
            teams: Optional[Iterable[str]] = None,
            filter_by: str = 'fppg',
    ):
        assert filter_by in ('fppg', 'efficiency', 'salary')
        self.from_value = from_value
        self.to_value = to_value
        self.positions = frozenset(positions or [])
        self.teams = frozenset(teams or [])
        self.filter_by = filter_by

    def filter(self, player, include_not_matched: bool = True) -> bool:
        if self.teams and player.team not in self.teams:
            return include_not_matched
        for position in self.positions:
            if position and position not in player.positions:
                return include_not_matched
        player_attr = getattr(player, self.filter_by)
        if player_attr < self.from_value:
            return False
        if self.to_value and player_attr > self.to_value:
            return False
        return True


class PlayerPool:
    def __init__(self, settings: BaseSettings):
        self._settings = settings
        self._remaining_positions = settings.positions[:]
        self._players: List[Player] = []
        self._players_by_name: DefaultDict[str, List[Player]] = defaultdict(list)
        self._players_by_id: Dict[str, Player] = {}
        self._exclude_teams: Set[str] = set()
        self._locked_players: Dict[Player, Optional[LineupPosition]] = {}
        self._player_filters: List[BaseFilter] = []
        self.with_injured = False
        self.search_threshold = 0.8
        self.removed_players: Set[Player] = set()

    @property
    def all_players(self) -> List[Player]:
        return self._players

    @property
    def filtered_players(self) -> List[Player]:
        pool = []
        for player in self._players:
            if (
                (player in self.removed_players) or
                (player.max_exposure is not None and player.max_exposure <= 0) or
                (not self.with_injured and player.is_injured) or
                player.team in self._exclude_teams or
                (self._player_filters and
                 not all(filter.filter(player) for filter in self._player_filters))
            ):
                continue
            pool.append(player)
        return pool

    @property
    def locked_players(self) -> List[Player]:
        return list(self._locked_players.keys())

    @property
    def locked_positions(self) -> List[LineupPosition]:
        return list(pos for pos in self._locked_players.values() if pos)

    @property
    def locked_players_with_positions(self) -> Dict[Player, LineupPosition]:
        return {player: position for player, position in self._locked_players.items() if position}

    @property
    def available_teams(self) -> FrozenSet[str]:
        return frozenset(player.team for player in self._players)

    @property
    def available_positions(self) -> FrozenSet[str]:
        return frozenset(chain.from_iterable(
            position.positions for position in self._settings.positions))

    @property
    def available_roster_spots(self) -> FrozenSet[str]:
        return frozenset(pos.name for pos in self._settings.positions)

    @property
    def total_players(self) -> int:
        return self._settings.get_total_players()

    @property
    def remaining_players(self) -> int:
        return self.total_players - len(self.locked_players)

    @property
    def remaining_positions(self) -> List[LineupPosition]:
        return self._remaining_positions

    @property
    def games(self) -> FrozenSet[GameInfo]:
        return frozenset(player.game_info for player in self.filtered_players if player.game_info)

    @property
    def budget(self) -> Optional[float]:
        return self._settings.budget

    @property
    def used_budget(self) -> float:
        return sum(player.salary for player in self.locked_players)

    @property
    def remaining_budget(self) -> Optional[float]:
        if self.budget is None:
            return None
        return self.budget - self.used_budget

    def reset_players(self) -> None:
        self._players = []
        self._players_by_name = defaultdict(list)
        self._players_by_id = {}
        self._exclude_teams = set()
        self.removed_players = set()
        self._locked_players = {}
        self._player_filters = []

    def reset_locked(self) -> None:
        self._locked_players = {}

    def load_players(self, players: Iterable[Player]) -> None:
        self.reset_players()
        self.extend_players(players)

    def extend_players(self, players: Iterable[Player]):
        for player in players:
            self.add_player(player)

    def add_player(self, player: Player):
        self._players.append(player)
        self._players_by_name[player.full_name].append(player)
        self._players_by_id[player.id] = player

    def get_player_by_name(
            self, player_name: str, position: Optional[str] = None,
            allowed_players: Optional[Set[Player]] = None,
    ) -> Optional[Player]:
        players = set(self._players_by_name.get(player_name, set()))
        if position:
            players = {player for player in players if position in player.positions}
        if allowed_players:
            players = players.intersection(allowed_players)
        if players:
            if len(players) > 1:
                raise LineupOptimizerException('More than 1 player is found for: %s' % player_name)
            return list(players)[0]
        if self.search_threshold:
            matched_players = self.get_players(PlayerFilter(positions=[position])) if position else self.all_players
            possibilities = [(player, ratio(player_name, player.full_name)) for player in matched_players]
            filtered_possibilities = filter(lambda pos: pos[1] >= self.search_threshold, possibilities)
            if filtered_possibilities:
                sorted_players = sorted(filtered_possibilities, key=lambda pos: -pos[1])
                return next(map(lambda player: player[0], sorted_players))  # typing: ignore
        return None

    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        return self._players_by_id.get(player_id)

    def exclude_teams(self, teams: Iterable[str]):
        self._exclude_teams = set(teams)

    def remove_player(self, player: DirtyPlayer):
        self.removed_players.add(self._clean_player(player))

    def restore_player(self, player: DirtyPlayer):
        try:
            self.removed_players.remove(self._clean_player(player))
        except KeyError:
            raise LineupOptimizerException('Player not removed!')

    def lock_player(self, player: DirtyPlayer, position: Optional[str] = None):
        player = self._clean_player(player)
        if player.max_exposure == 0:
            raise LineupOptimizerException('Can\'t add this player to line up! Player has max exposure set to 0.')
        if player in self._locked_players:
            raise LineupOptimizerException('This player already in your line up!')
        if self.remaining_budget and player.salary > self.remaining_budget:
            raise LineupOptimizerException('Can\'t add this player to line up! Your team is over budget!')
        if self.remaining_players < 1:
            raise LineupOptimizerException('Can\'t add this player to line up! You already select all %s players!' %
                                           len(self.locked_players))
        max_from_one_team = self._settings.max_from_one_team
        if max_from_one_team:
            from_same_team = len([p for p in self.locked_players if p.team == player.team])
            if from_same_team + 1 > max_from_one_team:
                raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                               max_from_one_team)
        position_for_player = None
        if position:
            if position not in self.available_positions:
                raise LineupOptimizerException(
                    'Position %s doesn\'t exist. Available positions are %s' %
                    (position, ','.join(self.available_positions))
                )
            for remaining_position in self._remaining_positions:
                if position:
                    if position == remaining_position.name:
                        position_for_player = remaining_position
                        break
            else:
                raise LineupOptimizerException('Position %s is filled.' % position)
            if not list_intersection(player.positions, position_for_player.positions):
                raise LineupOptimizerException('Player can\'t be set to position %s' % position)
        try:
            link_players_with_positions({player, *self._locked_players}, self._settings.positions)
        except LineupOptimizerException:
            raise LineupOptimizerException('You\'re already select all %s\'s' % '/'.join(player.positions))
        if position_for_player:
            self._remaining_positions.remove(position_for_player)
        self._locked_players[player] = position_for_player

    def unlock_player(self, player: DirtyPlayer):
        player = self._clean_player(player)
        if player not in self._locked_players:
            raise LineupOptimizerException('Player is not locked')
        position = self._locked_players[player]
        if position:
            self._remaining_positions.insert(0, position)
        del self._locked_players[player]

    def get_players(self, *players_and_groups: Union[DirtyPlayer, PlayerFilter]) -> List[Player]:
        players, filters = [], []
        for item in players_and_groups:
            if isinstance(item, BaseFilter):
                filters.append(item)
            else:
                players.append(item)
        allowed_players = None
        if filters:
            allowed_players = {
                player for player in self.all_players if
                all(player_filter.filter(player, False) for player_filter in filters)
            }
        if players:
            result = []
            for player in players:
                cleaned_player = self._clean_player(player, allowed_players=allowed_players)
                if cleaned_player:
                    result.append(cleaned_player)
            return result
        return list(allowed_players) if allowed_players else self.all_players

    def add_filters(self, *filters: BaseFilter):
        self._player_filters.extend(filters)

    def _clean_player(self, player: DirtyPlayer, allowed_players: Optional[Set[Player]] = None) -> Player:
        if not isinstance(player, Player):
            cleaned_player = self.get_player_by_id(player) or self.get_player_by_name(
                player, allowed_players=allowed_players)
            if not cleaned_player:
                raise LineupOptimizerException('%s is not found' % player)
            return cleaned_player
        return player

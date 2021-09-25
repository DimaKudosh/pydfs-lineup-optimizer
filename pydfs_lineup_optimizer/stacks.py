from abc import ABCMeta, abstractmethod
from math import floor
from uuid import uuid4
from typing import List, Optional, Tuple, Dict, Union, cast, TYPE_CHECKING
from itertools import chain
from collections import Counter, defaultdict
from pydfs_lineup_optimizer import Player
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName
from pydfs_lineup_optimizer.utils import get_players_grouped_by_teams, list_intersection


if TYPE_CHECKING:  # pragma: no cover
    from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer


class OptimizerGroup:
    def __init__(
            self,
            players: List[Player],
            min_from_group: Optional[int] = None,
            max_from_group: Optional[int] = None,
    ):
        self.players = players
        self.min_from_group = min_from_group
        self.max_from_group = max_from_group


class BaseGroup(metaclass=ABCMeta):
    def __init__(
            self,
            max_exposure: Optional[float] = None,
            depends_on: Optional[Player] = None,
            min_from_group: Optional[int] = None,
            max_from_group: Optional[int] = None,
            strict_depend: bool = True,
            parent: Optional['BaseGroup'] = None,
    ):
        self.uuid = uuid4()
        self.max_exposure = max_exposure
        self.parent = parent
        self.depends_on = depends_on
        self.strict_depend = strict_depend
        self.min_from_group = min_from_group
        self.max_from_group = max_from_group

    @abstractmethod
    def get_all_players_groups(self) -> List[OptimizerGroup]:
        pass


class PlayersGroup(BaseGroup):
    def __init__(
            self,
            players: List[Player],
            min_from_group: Optional[int] = None,
            max_from_group: Optional[int] = None,
            max_exposure: Optional[float] = None,
            depends_on: Optional[Player] = None,
            strict_depend: bool = True,
            parent: Optional[BaseGroup] = None,
    ):
        if min_from_group is None and max_from_group is None:
            min_from_group = len(players)
        super().__init__(
            max_exposure=max_exposure,
            parent=parent,
            min_from_group=min_from_group,
            max_from_group=max_from_group,
            depends_on=depends_on,
            strict_depend=strict_depend,
        )
        self.players = list(set(players))

    def get_all_players_groups(self) -> List[OptimizerGroup]:
        return [OptimizerGroup(self.players, self.min_from_group, self.max_from_group)]

    def __str__(self):
        return 'Group: %s' % ','.join(player.full_name for player in self.players)


class NestedPlayersGroup(BaseGroup):
    def __init__(
            self,
            groups: List[PlayersGroup],
            min_from_group: Optional[int] = None,
            max_from_group: Optional[int] = None,
            max_exposure: Optional[float] = None,
            parent: Optional[BaseGroup] = None,
    ):
        if min_from_group is None and max_from_group is None:
            min_from_group = len(groups)
        super().__init__(
            max_exposure=max_exposure,
            parent=parent,
            min_from_group=min_from_group,
            max_from_group=max_from_group,
        )
        self.groups = groups

    def get_all_players_groups(self) -> List[OptimizerGroup]:
        return list(chain.from_iterable(group.get_all_players_groups() for group in self.groups))


class OptimizerStack:
    def __init__(self, groups: List[BaseGroup], can_intersect=False):
        self.groups = groups
        self.uuid = uuid4()
        self.can_intersect = can_intersect

    @property
    def with_exposures(self) -> bool:
        return any(group.max_exposure is not None for group in self.groups)


class BaseStack(metaclass=ABCMeta):
    @abstractmethod
    def validate(self, optimizer: 'LineupOptimizer') -> None:
        pass

    @abstractmethod
    def build_stacks(self, players: List[Player], optimizer: 'LineupOptimizer') -> List[OptimizerStack]:
        pass


class Stack(BaseStack):
    def __init__(self, groups: List[BaseGroup]):
        self.groups = groups

    def build_stacks(self, players: List[Player], optimizer: 'LineupOptimizer') -> List[OptimizerStack]:
        return [OptimizerStack(groups=self.groups)]

    def validate(self, optimizer: 'LineupOptimizer') -> None:
        pass


class TeamStack(BaseStack):
    def __init__(
            self,
            size: int,
            for_teams: Optional[List[str]] = None,
            for_positions: Optional[List[str]] = None,
            spacing: Optional[int] = None,
            max_exposure: Optional[float] = None,
            max_exposure_per_team: Optional[Dict[str, float]] = None,
    ):
        self.size = size
        self.for_teams = for_teams
        self.for_positions = for_positions
        self.spacing = spacing
        self.max_exposure = max_exposure
        self.max_exposure_per_team = max_exposure_per_team or {}

    def build_stacks(self, players: List[Player], optimizer: 'LineupOptimizer') -> List[OptimizerStack]:
        players_by_teams = get_players_grouped_by_teams(
            players, for_teams=self.for_teams, for_positions=self.for_positions)
        groups = []  # type: List[BaseGroup]
        spacing_groups = []  # type: List[BaseGroup]
        for team, players in players_by_teams.items():
            parent_group = PlayersGroup(
                players=players,
                min_from_group=self.size,
                max_exposure=self.max_exposure_per_team.get(team, self.max_exposure)
            )
            groups.append(parent_group)
            if not self.spacing:
                continue
            players_by_roster_positions = defaultdict(list)  # type: Dict[int, List[Player]]
            for player in players:
                if player.roster_order is None:
                    continue
                players_by_roster_positions[player.roster_order].append(player)
            if not players_by_roster_positions:
                continue
            all_allowed_roster_orders = set()
            max_spacing = max(players_by_roster_positions.keys())
            for roster_position in players_by_roster_positions.keys():
                allowed_roster_orders = []
                for i in range(self.spacing):
                    if roster_position + i <= max_spacing:
                        allowed_roster_orders.append(roster_position + i)
                    else:
                        allowed_roster_orders.append(((roster_position + i) % (max_spacing + 1)) + 1)
                all_allowed_roster_orders.add(tuple(sorted(allowed_roster_orders)))
            for roster_orders in all_allowed_roster_orders:
                spacing_groups.append(PlayersGroup(
                    players=list(chain.from_iterable(
                        players for players_spacing, players in players_by_roster_positions.items()
                        if players_spacing in roster_orders
                    )),
                    min_from_group=self.size,
                    parent=parent_group,
                ))
        stacks = [OptimizerStack(groups=groups)]
        if spacing_groups:
            stacks.append(OptimizerStack(groups=spacing_groups, can_intersect=True))
        return stacks

    def validate(self, optimizer: 'LineupOptimizer') -> None:
        settings = optimizer.settings
        max_from_one_team = settings.max_from_one_team or settings.get_total_players()
        if self.size > max_from_one_team:
            raise LineupOptimizerException(
                'Stack size should be smaller than max players from one team (%d)' % max_from_one_team)
        for team in self.for_teams or []:
            if team not in optimizer.available_teams:
                raise LineupOptimizerIncorrectTeamName('%s is incorrect team name.' % team)
        for position in self.for_positions or []:
            if position not in optimizer.player_pool.available_positions:
                raise LineupOptimizerIncorrectPositionName('%s is incorrect position name.' % position)


class PositionsStack(BaseStack):
    def __init__(
            self,
            positions: List[Union[str, Tuple[str, ...]]],
            for_teams: Optional[List[str]] = None,
            max_exposure: Optional[float] = None,
            max_exposure_per_team: Optional[Dict[str, float]] = None,
    ):
        formatted_positions_stacks = tuple(
            [cast(Tuple[str, ...], (position,) if isinstance(position, str) else tuple(position))
             for position in positions]
        )
        self.positions = formatted_positions_stacks
        self.for_teams = for_teams
        self.max_exposure = max_exposure
        self.max_exposure_per_team = max_exposure_per_team or {}

    def build_stacks(self, players: List[Player], optimizer: 'LineupOptimizer') -> List[OptimizerStack]:
        players_by_teams = get_players_grouped_by_teams(players, for_teams=self.for_teams)
        all_positions = tuple(set(chain.from_iterable(self.positions)))
        positions_for_optimizer = Counter(self.positions)
        positions_for_optimizer[all_positions] = len(self.positions)
        all_groups = []  # type: List[BaseGroup]
        for team_name, team_players in players_by_teams.items():
            groups = []
            for positions, total in positions_for_optimizer.items():
                groups.append(PlayersGroup(
                    players=[player for player in team_players if list_intersection(player.positions, positions)],
                    min_from_group=total,
                ))
            nested_group = NestedPlayersGroup(
                groups=groups,
                max_exposure=self.max_exposure_per_team.get(team_name, self.max_exposure),
            )
            all_groups.append(nested_group)
        return [OptimizerStack(groups=all_groups)]

    def validate(self, optimizer: 'LineupOptimizer') -> None:
        if not self.positions or not all(self.positions):
            raise LineupOptimizerException('Positions stack can\'t be empty')
        settings = optimizer.settings
        max_from_one_team = settings.max_from_one_team or settings.get_total_players()
        if len(self.positions) > max_from_one_team:
            raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                           max_from_one_team)
        for position in set(chain.from_iterable(self.positions)):
            if position not in optimizer.player_pool.available_positions:
                raise LineupOptimizerIncorrectPositionName('%s is incorrect position name.' % position)
        for team in self.for_teams or []:
            if team not in optimizer.player_pool.available_teams:
                raise LineupOptimizerIncorrectTeamName('%s is incorrect team name.' % team)


class GameStack(BaseStack):
    def __init__(
            self,
            size: int,
            max_exposure: Optional[float] = None,
            min_from_team: int = 1,
    ):
        self.size = size
        self.max_exposure = max_exposure
        self.min_from_team = min_from_team

    def build_stacks(self, players, optimizer):
        players_by_teams = get_players_grouped_by_teams(players)
        all_groups: List[BaseGroup] = []
        for game in optimizer.games:
            groups = [PlayersGroup(
                players=players_by_teams[game.home_team],
                min_from_group=self.min_from_team,
            ), PlayersGroup(
                players=players_by_teams[game.away_team],
                min_from_group=self.min_from_team,
            ), PlayersGroup(
                players=[*players_by_teams[game.home_team], *players_by_teams[game.away_team]],
                min_from_group=self.size,
            )]
            nested_group = NestedPlayersGroup(
                groups=groups,
                max_exposure=self.max_exposure,
            )
            all_groups.append(nested_group)
        return [OptimizerStack(groups=all_groups)]

    def validate(self, optimizer) -> None:
        if floor(self.size / 2) < self.min_from_team:
            raise LineupOptimizerException('min_from_team is greater than stack size')

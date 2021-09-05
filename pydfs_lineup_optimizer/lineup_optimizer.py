from collections import OrderedDict
from itertools import chain
from math import ceil
from typing import FrozenSet, Type, Generator, Tuple, Optional, List, Dict, Set, Iterable
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.solvers import Solver, SolverInfeasibleSolutionException
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName, GenerateLineupException
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.settings import BaseSettings
from pydfs_lineup_optimizer.player import Player, LineupPlayer, GameInfo
from pydfs_lineup_optimizer.utils import ratio, link_players_with_positions, get_remaining_positions, \
    show_deprecation_warning
from pydfs_lineup_optimizer.rules import *
from pydfs_lineup_optimizer.stacks import BaseGroup, BaseStack, Stack
from pydfs_lineup_optimizer.context import OptimizationContext
from pydfs_lineup_optimizer.statistics import Statistic
from pydfs_lineup_optimizer.exposure_strategy import BaseExposureStrategy, TotalExposureStrategy
from pydfs_lineup_optimizer.fantasy_points_strategy import BaseFantasyPointsStrategy, StandardFantasyPointsStrategy, \
    RandomFantasyPointsStrategy
from pydfs_lineup_optimizer.solvers import get_default_solver
from pydfs_lineup_optimizer.player_pool import PlayerPool


BASE_RULES = {
    TotalPlayersRule, LineupBudgetRule, PositionsRule, MaxFromOneTeamRule, LockedPlayersRule,
    UniquePlayerRule, UniqueLineupRule, TotalTeamsRule, GenericStacksRule, MinExposureRule, MinGamesRule,
}


class LineupOptimizer:
    def __init__(self, settings: Type[BaseSettings], solver: Type[Solver] = get_default_solver()):
        self._settings = settings()
        self.player_pool = PlayerPool(self._settings)
        self._csv_importer = None  # type: Optional[Type[CSVImporter]]
        self._rules = BASE_RULES.copy()  # type: Set[Type[OptimizerRule]]
        self._min_deviation = 0.0
        self._max_deviation = 0.12
        self.players_from_one_team = {}  # type: Dict[str, int]
        self.players_with_same_position = {}  # type: Dict[str, int]
        self.min_salary_cap = None  # type: Optional[float]
        self.max_repeating_players = None  # type: Optional[int]
        self._solver_class = solver
        self.max_projected_ownership = None  # type: Optional[float]
        self.min_projected_ownership = None  # type: Optional[float]
        self.opposing_teams_position_restriction = None  # type: Optional[Tuple[List[str], List[str]]]
        self.spacing_positions = None  # type: Optional[List[str]]
        self.spacing = None  # type: Optional[int]
        self.default_team_exposure = None  # type: Optional[float]
        self.teams_exposures = None  # type: Optional[Dict[str, float]]
        self.teams_exposure_strategy = None  # type: Optional[Type[BaseExposureStrategy]]
        self.team_stacks_for_positions = None  # type: Optional[List[str]]
        self.same_team_restrict_positions = None  # type: Optional[Tuple[Tuple[str, str], ...]]
        self.opposing_team_force_positions = None  # type: Optional[Tuple[Tuple[str, str], ...]]
        self.opposing_teams_max_allowed = 0
        self.min_teams = None  # type: Optional[int]
        self.max_teams = None  # type: Optional[int]
        self.stacks = []  # type: List[BaseStack]
        self.min_starters = None  # type: Optional[int]
        self.last_context = None  # type: Optional[OptimizationContext]
        self.fantasy_points_strategy = StandardFantasyPointsStrategy()  # type: BaseFantasyPointsStrategy

    @property
    def budget(self) -> Optional[float]:
        return self._settings.budget

    @property
    def total_players(self) -> int:
        show_deprecation_warning('total_players will be removed in version 3.7, use player_pool.total_players instead')
        return self.player_pool.total_players

    @property
    def remaining_budget(self) -> Optional[float]:
        show_deprecation_warning('remaining_budget will be removed in version 3.7, '
                                 'use player_pool.remaining_budget instead')
        return self.player_pool.remaining_budget

    @property
    def remaining_players(self) -> int:
        show_deprecation_warning('remaining_players will be removed in version 3.7, '
                                 'use player_pool.remaining_players instead')
        return self.player_pool.remaining_players

    @property
    def max_from_one_team(self) -> Optional[int]:
        return self._settings.max_from_one_team

    @property
    def available_teams(self) -> FrozenSet[str]:
        show_deprecation_warning('available_teams will be removed in version 3.7, '
                                 'use player_pool.available_teams instead')
        return self.player_pool.available_teams

    @property
    def available_positions(self) -> FrozenSet[str]:
        show_deprecation_warning('available_positions will be removed in version 3.7, '
                                 'use player_pool.available_positions instead')
        return self.player_pool.available_positions

    @property
    def removed_players(self) -> Set[Player]:
        show_deprecation_warning('removed_players will be removed in version 3.7, '
                                 'use player_pool.removed_players instead')
        return self.player_pool.removed_players

    @property
    def players(self) -> List[Player]:
        show_deprecation_warning('players will be removed in version 3.7, '
                                 'use player_pool.filtered_players instead')
        return self.player_pool.filtered_players

    @property
    def locked_players(self) -> List[Player]:
        show_deprecation_warning('locked_players will be removed in version 3.7, use player_pool.locked_players instead')
        return self.player_pool.locked_players

    @property
    def settings(self) -> BaseSettings:
        return self._settings

    @property
    def games(self) -> FrozenSet[GameInfo]:
        show_deprecation_warning('games will be removed in version 3.7, use player_pool.games instead')
        return self.player_pool.games

    def reset_lineup(self):
        show_deprecation_warning('reset_lineup will be removed in version 3.7, use player_pool.reset_locked instead')
        self.player_pool.reset_locked()

    def set_fantasy_points_strategy(self, strategy: BaseFantasyPointsStrategy):
        self.fantasy_points_strategy = strategy

    def set_deviation(self, min_deviation: float, max_deviation: float):
        """
        Set deviation ranges for randomness mode
        """
        show_deprecation_warning('set_deviation method is deprecated and will be removed in 3.6, '
                                 'set deviation in  RandomFantasyPointsStrategy instead')
        self._min_deviation = min_deviation
        self._max_deviation = max_deviation

    def get_deviation(self) -> Tuple[float, float]:
        return self._min_deviation, self._max_deviation

    def set_csv_importer(self, csv_importer: Type[CSVImporter]):
        self._csv_importer = csv_importer

    def set_min_salary_cap(self, min_salary: float):
        if self.budget and min_salary > self.budget:
            raise LineupOptimizerException('Min salary greater than max budget')
        self.add_new_rule(MinSalaryCapRule)
        self.min_salary_cap = min_salary

    def load_players_from_csv(self, filename: str):
        """
        Load player list from CSV file with passed filename.
        """
        csv_importer = self._csv_importer
        if not csv_importer:
            csv_importer = self._settings.csv_importer
        self.player_pool.extend_players(csv_importer(filename).import_players())

    def load_lineups_from_csv(self, filename: str) -> List[Lineup]:
        csv_importer = self._csv_importer
        if not csv_importer:
            csv_importer = self._settings.csv_importer
        return csv_importer(filename).import_lineups(self.player_pool.all_players)

    def load_players(self, players: List[Player]):
        show_deprecation_warning('load_players will be removed in version 3.7, use player_pool.load_players instead')
        self.player_pool.load_players(players)

    def extend_players(self, players: List[Player]):
        show_deprecation_warning('extend_players will be removed in version 3.7, use player_pool.extend_players instead')
        self.player_pool.extend_players(players)

    def add_new_rule(self, rule: Type[OptimizerRule]):
        self._rules.add(rule)

    def remove_rule(self, rule: Type[OptimizerRule], silent: bool = True):
        try:
            self._rules.remove(rule)
        except KeyError:
            if not silent:
                raise LineupOptimizerException('Rule isn\'t added!')

    def remove_player(self, player: Player):
        show_deprecation_warning('remove_player will be removed in version 3.7, use player_pool.remove_player instead')
        self.player_pool.remove_player(player)

    def restore_player(self, player: Player):
        show_deprecation_warning('restore_player will be removed in version 3.7, use player_pool.restore_player instead')
        self.player_pool.restore_player(player)

    def find_players(self, name: str) -> List[Player]:
        """
        Return list of players with similar name.
        """
        show_deprecation_warning('find_players will be removed in version 3.7')
        player_pool = self.player_pool
        possibilities = [(player, ratio(name, player.full_name)) for player in player_pool.all_players]
        filtered_possibilities = filter(lambda pos: pos[1] >= player_pool.search_threshold, possibilities)
        players = sorted(filtered_possibilities, key=lambda pos: -pos[1])
        return list(map(lambda p: p[0], players))

    def get_player_by_name(self, name: str) -> Optional[Player]:
        show_deprecation_warning('get_player_by_name will be removed in version 3.7, '
                                 'use player_pool.get_player_by_name instead')
        return self.player_pool.get_player_by_name(name)

    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        show_deprecation_warning('get_player_by_id will be removed in version 3.7, '
                                 'use player_pool.get_player_by_id instead')
        return self.player_pool.get_player_by_id(player_id)

    def add_player_to_lineup(self, player: Player):
        show_deprecation_warning('add_player_to_lineup will be removed in version 3.7, '
                                 'use player_pool.lock_player instead')
        self.player_pool.lock_player(player)

    def remove_player_from_lineup(self, player: Player):
        show_deprecation_warning('remove_player_from_lineup will be removed in version 3.7, '
                                 'use player_pool.unlock_player instead')
        self.player_pool.unlock_player(player)

    def set_players_from_one_team(self, teams: Optional[Dict[str, int]] = None):
        if teams is not None:
            teams = {team: num_of_players for team, num_of_players in teams.items()}
            for team, num_of_players in teams.items():
                self._check_team_constraint(team, num_of_players)
            self.add_new_rule(TeamMatesRule)
        else:
            self.remove_rule(TeamMatesRule)
        self.players_from_one_team = teams or {}

    def set_players_with_same_position(self, positions: Dict[str, int]):
        positions = positions or {}
        positions = {position.upper(): num_of_players for position, num_of_players in positions.items()}
        for pos, val in positions.items():
            self._check_position_constraint(pos)
        self.players_with_same_position = positions

    def set_max_repeating_players(self, max_repeating_players: int):
        if max_repeating_players >= self.player_pool.total_players:
            raise LineupOptimizerException('Maximum repeating players should be smaller than %d' %
                                           self.player_pool.total_players)
        elif max_repeating_players < 1:
            raise LineupOptimizerException('Maximum repeating players should be 1 or greater')
        self.max_repeating_players = max_repeating_players

    def set_projected_ownership(
            self,
            min_projected_ownership: Optional[float] = None,
            max_projected_ownership: Optional[float] = None
    ):
        if min_projected_ownership and max_projected_ownership and min_projected_ownership >= max_projected_ownership:
            raise LineupOptimizerException('Max projected ownership should be greater than min projected ownership')
        self.max_projected_ownership = max_projected_ownership / 100 if \
            max_projected_ownership and max_projected_ownership > 1 else max_projected_ownership
        self.min_projected_ownership = min_projected_ownership / 100 if \
            min_projected_ownership and min_projected_ownership > 1 else min_projected_ownership
        if max_projected_ownership or min_projected_ownership:
            self.add_new_rule(ProjectedOwnershipRule)
        else:
            self.remove_rule(ProjectedOwnershipRule)

    def restrict_positions_for_opposing_team(
            self,
            first_team_positions: List[str],
            second_team_positions: List[str],
            max_allowed: int = 0,
    ):
        if not self.player_pool.games:
            raise LineupOptimizerException('Game Info isn\'t specified for players')
        self.opposing_teams_position_restriction = (first_team_positions, second_team_positions)
        self.opposing_teams_max_allowed = max_allowed
        self.add_new_rule(RestrictPositionsForOpposingTeam)

    def restrict_positions_for_same_team(self, *restrict_positions: Tuple[str, str]):
        if not all(len(positions) == 2 for positions in restrict_positions):
            raise LineupOptimizerException('Exactly 2 positions must be specified in restrict positions')
        for position in set(chain.from_iterable(restrict_positions)):
            self._check_position_constraint(position)
        self.same_team_restrict_positions = restrict_positions
        self.add_new_rule(RestrictPositionsForSameTeamRule)

    def force_positions_for_opposing_team(self, *force_positions: Tuple[str, str]):
        if not all(len(positions) == 2 for positions in force_positions):
            raise LineupOptimizerException('Exactly 2 positions must be specified in force positions')
        for position in set(chain.from_iterable(force_positions)):
            self._check_position_constraint(position)
        self.opposing_team_force_positions = force_positions
        self.add_new_rule(ForcePositionsForOpposingTeamRule)

    def set_spacing_for_positions(self, positions: List[str], spacing: int):
        if spacing < 1:
            raise LineupOptimizerException('Spacing must be 1 or greater')
        available_positions = self.player_pool.available_positions
        if any(position not in available_positions for position in positions):
            raise LineupOptimizerException('Incorrect positions. Choices are: %s' % available_positions)
        self.spacing_positions = positions
        self.spacing = spacing
        self.add_new_rule(RosterSpacingRule)

    def set_total_teams(self, total_teams: Optional[int] = None, min_teams: Optional[int] = None,
                        max_teams: Optional[int] = None):
        if not any((total_teams, min_teams, max_teams)):
            raise LineupOptimizerException('At least one parameter should be passed')
        if total_teams:
            min_teams = total_teams
            max_teams = total_teams
            show_deprecation_warning('total_teams parameter is replaced with min_teams/max_teams parameters and '
                                     'will be removed in version 3.7')
        available_teams = len(self.player_pool.available_teams)
        if min_teams is not None and max_teams is not None and min_teams > max_teams:
            raise LineupOptimizerException('min_teams can\'t be greater than max_teams')
        if (min_teams is not None and min_teams > available_teams) or \
                (max_teams is not None and max_teams > available_teams):
            raise LineupOptimizerException('Only %d teams available' % available_teams)
        total_players = self.settings.get_total_players()
        settings_min_teams = self.settings.min_teams
        max_from_one_team = self.settings.max_from_one_team
        if not settings_min_teams and max_from_one_team:
            settings_min_teams = ceil(total_players / max_from_one_team)
        if settings_min_teams and ((
            max_teams is not None and max_teams < settings_min_teams
        ) or (
            min_teams is not None and min_teams < settings_min_teams
        )):
            raise LineupOptimizerException('Minimum number of teams is %d' % settings_min_teams)
        if (min_teams is not None and min_teams > total_players) or \
                (max_teams is not None and max_teams > total_players):
            raise LineupOptimizerException('Maximum number of teams is %d' % total_players)
        self.min_teams = min_teams
        self.max_teams = max_teams

    def add_players_group(self, group: BaseGroup) -> None:
        stack = Stack(groups=[group])
        self.stacks.append(stack)

    def add_stack(self, stack: BaseStack) -> None:
        stack.validate(self)
        self.stacks.append(stack)

    def reset_stacks(self) -> None:
        self.stacks = []

    def set_min_starters(self, min_starters: int) -> None:
        if min_starters > self.settings.get_total_players():
            raise LineupOptimizerException('Num of starters can\'t be greater than max players')
        if min_starters > len([p for p in self.player_pool.filtered_players if p.is_confirmed_starter]):
            raise LineupOptimizerException('Num of starters can\'t be greater than max starters')
        self.min_starters = min_starters
        self.add_new_rule(MinStartersRule)

    def set_teams_max_exposures(
            self,
            default_max_exposure: Optional[float] = None,
            exposures_by_team: Optional[Dict[str, float]] = None,
            exposure_strategy: Optional[Type[BaseExposureStrategy]] = TotalExposureStrategy,
    ):
        if exposures_by_team:
            for team in exposures_by_team:
                if team not in self.player_pool.available_teams:
                    raise LineupOptimizerException('Unknown team: %s' % team)
        self.default_team_exposure = default_max_exposure
        self.teams_exposures = exposures_by_team
        self.teams_exposure_strategy = exposure_strategy
        if default_max_exposure or exposures_by_team:
            self.add_new_rule(TeamsExposureRule)
        else:
            self.remove_rule(TeamsExposureRule)

    def optimize(
            self,
            n: int,
            max_exposure: Optional[float] = None,
            randomness: bool = False,
            with_injured: Optional[bool] = None,
            exposure_strategy: Type[BaseExposureStrategy] = TotalExposureStrategy,
            exclude_lineups: Optional[Iterable[Lineup]] = None,
    ) -> Generator[Lineup, None, None]:
        if with_injured is not None:
            show_deprecation_warning('with_injured parameter is deprecated, use player_pool.with_injured instead')
            self.player_pool.with_injured = with_injured
        players = self.player_pool.filtered_players
        context = OptimizationContext(
            total_lineups=n,
            players=players,
            max_exposure=max_exposure,
            randomness=randomness,
            exposure_strategy=exposure_strategy,
            exclude_lineups=exclude_lineups or [],
        )
        rules = self._rules.copy()
        rules.update(self.settings.extra_rules)
        if randomness:
            show_deprecation_warning('Randomness parameter is deprecated and will be removed in 3.6, '
                                     'use set_fantasy_points_strategy instead')
            self.set_fantasy_points_strategy(RandomFantasyPointsStrategy(self._min_deviation, self._max_deviation))
        rules.add(Objective)
        base_solver = self._solver_class()
        base_solver.setup_solver()
        players_dict = OrderedDict(
            [(player, base_solver.add_variable(base_solver.build_player_var_name(player, str(i))))
             for i, player in enumerate(players)])
        variables_dict = {v: k for k, v in players_dict.items()}
        constraints = [constraint(self, players_dict, context) for constraint in rules]
        for constraint in constraints:
            constraint.apply(base_solver)
        previous_lineup = None
        for _ in range(n):
            solver = base_solver.copy()  # type: Solver
            for constraint in constraints:
                constraint.apply_for_iteration(solver, previous_lineup)
            try:
                solved_variables = solver.solve()
                lineup_players = []
                variables_names = []
                for solved_variable in solved_variables:
                    player = variables_dict.get(solved_variable)
                    if player:
                        lineup_players.append(player)
                    variables_names.append(solved_variable.name)
                lineup = self._build_lineup(lineup_players, context)
                previous_lineup = lineup
                context.add_lineup(lineup)
                yield lineup
                total_players = self.player_pool.total_players
                if total_players and len(self.player_pool.locked_players) == total_players:
                    return
                for constraint in constraints:
                    constraint.post_optimize(variables_names)
            except SolverInfeasibleSolutionException as solver_exception:
                raise GenerateLineupException(solver_exception.get_user_defined_constraints())
        self.last_context = context

    def optimize_lineups(
            self,
            lineups: List[Lineup],
            max_exposure: Optional[float] = None,
            randomness: bool = False,
            with_injured: bool = None,
            exposure_strategy: Type[BaseExposureStrategy] = TotalExposureStrategy
    ):
        if with_injured is not None:
            show_deprecation_warning('with_injured parameter is deprecated, use player_pool.with_injured instead')
            self.player_pool.with_injured = with_injured
        players = self.player_pool.filtered_players
        context = OptimizationContext(
            total_lineups=len(lineups),
            players=players,
            existed_lineups=lineups,
            max_exposure=max_exposure,
            randomness=randomness,
            exposure_strategy=exposure_strategy
        )
        rules = self._rules.copy()
        rules.update(self.settings.extra_rules)
        if randomness:
            show_deprecation_warning('Randomness parameter is deprecated and will be removed in 3.6, '
                                     'use set_fantasy_points_strategy instead')
            self.set_fantasy_points_strategy(RandomFantasyPointsStrategy(self._min_deviation, self._max_deviation))
        rules.add(Objective)
        rules.add(LateSwapRule)
        rules.remove(PositionsRule)
        base_solver = self._solver_class()
        base_solver.setup_solver()
        players_dict = OrderedDict(
            [(player, base_solver.add_variable(base_solver.build_player_var_name(player, str(i))))
             for i, player in enumerate(players)])
        variables_dict = {v: k for k, v in players_dict.items()}
        constraints = [constraint(self, players_dict, context) for constraint in rules]
        for constraint in constraints:
            constraint.apply(base_solver)
        previous_lineup = None
        for lineup in lineups:
            if len(lineup.get_unswappable_players()) == self.total_players:
                yield lineup
                continue
            solver = base_solver.copy()  # type: Solver
            for constraint in constraints:
                constraint.apply_for_iteration(solver, previous_lineup)
            try:
                solved_variables = solver.solve()
                unswappable_players = lineup.get_unswappable_players()
                lineup_players = []
                variables_names = []
                for solved_variable in solved_variables:
                    player = variables_dict.get(solved_variable)
                    if player:
                        lineup_players.append(player)
                    variables_names.append(solved_variable.name)
                generated_lineup = self._build_lineup(lineup_players, context, unswappable_players)
                previous_lineup = generated_lineup
                context.add_lineup(generated_lineup)
                yield generated_lineup
                for constraint in constraints:
                    constraint.post_optimize(variables_names)
            except SolverInfeasibleSolutionException as solver_exception:
                raise GenerateLineupException(solver_exception.get_user_defined_constraints())
        self.last_context = context

    def print_statistic(self, with_excluded: bool = True) -> None:
        if self.last_context is None:
            raise LineupOptimizerException('You should generate lineups before printing statistic')
        Statistic(self, with_excluded).print_report()

    def export(self, filename: str, with_excluded: bool = True) -> None:
        if self.last_context is None:
            raise LineupOptimizerException('You should generate lineups before printing statistic')
        self.settings.csv_exporter(self.last_context.get_lineups(with_excluded)).export(filename)

    def _build_lineup(
            self,
            players: List[Player],
            context: OptimizationContext,
            unswappable_players: Optional[List[LineupPlayer]] = None,
    ) -> Lineup:
        lineup = []
        positions = self._settings.positions[:]
        if not positions:
            for player in sorted(players, key=lambda p: p.positions[0]):
                lineup.append(LineupPlayer(player, player.positions[0], used_fppg=context.players_used_fppg.get(player)))
            return Lineup(lineup, self._settings.lineup_printer)
        if unswappable_players:
            players = [player for player in players if player not in unswappable_players]
            positions = get_remaining_positions(positions, unswappable_players)
            lineup.extend(unswappable_players)
        for locked_player, locked_position in self.player_pool.locked_players_with_positions.items():
            players.remove(locked_player)
            positions.remove(locked_position)
            lineup.append(LineupPlayer(locked_player, locked_position.name))
        players_with_positions = link_players_with_positions(players, positions)
        for player, position in players_with_positions.items():
            lineup.append(LineupPlayer(player, position.name, used_fppg=context.players_used_fppg.get(player)))
        positions_order = [pos.name for pos in self._settings.positions]
        lineup.sort(key=lambda p: positions_order.index(p.lineup_position))
        return Lineup(lineup, self._settings.lineup_printer)

    def _check_team_constraint(self, team: str, num_of_players: int):
        if team not in self.player_pool.available_teams:
            raise LineupOptimizerIncorrectTeamName('%s is incorrect team name. Choices are [%s]' %
                                                   (team, ','.join(self.player_pool.available_teams)))
        if self.max_from_one_team and num_of_players > self.max_from_one_team:
            raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                           self.max_from_one_team)

    def _check_position_constraint(self, position: str):
        if position not in self.player_pool.available_positions:
            raise LineupOptimizerIncorrectPositionName('%s is incorrect position name. Choices are [%s]' %
                                                       (position, ','.join(self.player_pool.available_positions)))

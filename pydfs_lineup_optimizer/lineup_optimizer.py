import warnings
from collections import OrderedDict
from itertools import chain
from math import ceil
from typing import FrozenSet, Type, Generator, Tuple, Union, Optional, List, Dict, Set, cast
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.solvers import Solver, PuLPSolver, SolverException
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.settings import BaseSettings
from pydfs_lineup_optimizer.player import Player, LineupPlayer, GameInfo
from pydfs_lineup_optimizer.utils import ratio, link_players_with_positions, process_percents, get_remaining_positions
from pydfs_lineup_optimizer.rules import *
from pydfs_lineup_optimizer.stacks import BaseGroup, TeamStack, PositionsStack, BaseStack, Stack
from pydfs_lineup_optimizer.context import OptimizationContext
from pydfs_lineup_optimizer.statistics import Statistic
from pydfs_lineup_optimizer.exposure_strategy import BaseExposureStrategy, TotalExposureStrategy


BASE_RULES = {TotalPlayersRule, LineupBudgetRule, PositionsRule, MaxFromOneTeamRule, LockedPlayersRule,
              RemoveInjuredRule, UniquePlayerRule, UniqueLineupRule, TotalTeamsRule, GenericStacksRule,
              MinExposureRule, MinGamesRule}


class LineupOptimizer:
    def __init__(self, settings: Type[BaseSettings], solver: Type[Solver] = PuLPSolver):
        self._settings = settings()
        self._csv_importer = None  # type: Optional[Type[CSVImporter]]
        self._rules = BASE_RULES.copy()  # type: Set[Type[OptimizerRule]]
        self._players = []  # type: List[Player]
        self._lineup = []  # type: List[Player]
        self._available_positions = frozenset(chain.from_iterable(
            position.positions for position in self._settings.positions))
        self._removed_players = []  # type: List[Player]
        self._search_threshold = 0.8
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
        self.teams_exposures = None  # type: Optional[Dict[str, float]]
        self.team_stacks_for_positions = None  # type: Optional[List[str]]
        self.same_team_restrict_positions = None  # type: Optional[Tuple[Tuple[str, str], ...]]
        self.opposing_team_force_positions = None  # type: Optional[Tuple[Tuple[str, str], ...]]
        self.opposing_teams_max_allowed = 0
        self.total_teams = None  # type: Optional[int]
        self.stacks = []  # type: List[BaseStack]
        self.min_starters = None  # type: Optional[int]
        self.last_context = None  # type: Optional[OptimizationContext]

    @property
    def budget(self) -> Optional[float]:
        return self._settings.budget

    @property
    def total_players(self) -> int:
        return self._settings.get_total_players()

    @property
    def remaining_budget(self) -> Optional[float]:
        if self.budget is None:
            return None
        return self.budget - sum(player.salary for player in self.locked_players)

    @property
    def remaining_players(self) -> int:
        return self.total_players - len(self.locked_players)

    @property
    def max_from_one_team(self) -> Optional[int]:
        return self._settings.max_from_one_team

    @property
    def available_teams(self) -> FrozenSet[str]:
        return frozenset([p.team for p in self._players])

    @property
    def available_positions(self) -> FrozenSet[str]:
        return self._available_positions

    @property
    def removed_players(self) -> List[Player]:
        return self._removed_players

    @property
    def players(self) -> List[Player]:
        return [player for player in self._players if player not in self.removed_players]

    @property
    def locked_players(self) -> List[Player]:
        return self._lineup

    @property
    def settings(self) -> BaseSettings:
        return self._settings

    @property
    def games(self) -> FrozenSet[GameInfo]:
        return frozenset(player.game_info for player in self.players if player.game_info)

    def reset_lineup(self):
        self._lineup = []

    def set_deviation(self, min_deviation: float, max_deviation: float):
        """
        Set deviation ranges for randomness mode
        """
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
        self._players = csv_importer(filename).import_players()

    def load_lineups_from_csv(self, filename: str) -> List[Lineup]:
        csv_importer = self._csv_importer
        if not csv_importer:
            csv_importer = self._settings.csv_importer
        return csv_importer(filename).import_lineups(self.players)

    def load_players(self, players: List[Player]):
        """
        Manually load player to optimizer
        """
        self._players = players

    def extend_players(self, players: List[Player]):
        """
        Add more players for current optimizer players
        """
        self._players.extend(players)

    def add_new_rule(self, rule: Type[OptimizerRule]):
        self._rules.add(rule)

    def remove_rule(self, rule: Type[OptimizerRule], silent: bool = True):
        try:
            self._rules.remove(rule)
        except KeyError:
            if not silent:
                raise LineupOptimizerException('Rule isn\'t added!')

    def remove_player(self, player: Player):
        """
        Remove player from players list used for optimization
        """
        self._removed_players.append(player)

    def restore_player(self, player: Player):
        """
        Restore removed player.
        """
        try:
            self._removed_players.remove(player)
        except ValueError:
            raise LineupOptimizerException('Player not removed!')

    def find_players(self, name: str) -> List[Player]:
        """
        Return list of players with similar name.
        """
        possibilities = [(player, ratio(name, player.full_name)) for player in self._players]
        filtered_possibilities = filter(lambda pos: pos[1] >= self._search_threshold, possibilities)
        players = sorted(filtered_possibilities, key=lambda pos: -pos[1])
        return list(map(lambda p: p[0], players))

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """
        Return closest player with similar name or None.
        """
        players = self.find_players(name)
        return players[0] if players else None

    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        for player in self._players:
            if player.id == player_id:
                return player
        return None

    def add_player_to_lineup(self, player: Player):
        """
        Force add specified player to lineup.
        Return true if player successfully added to lineup.
        """
        if player.max_exposure == 0:
            raise LineupOptimizerException('Can\'t add this player to line up! Player has max exposure set to 0.')
        if player in self._lineup:
            raise LineupOptimizerException('This player already in your line up!')
        if self.remaining_budget and player.salary > self.remaining_budget:
            raise LineupOptimizerException('Can\'t add this player to line up! Your team is over budget!')
        if self.remaining_players < 1:
            raise LineupOptimizerException('Can\'t add this player to line up! You already select all %s players!' %
                                           len(self.locked_players))
        if self.max_from_one_team:
            from_same_team = len([p for p in self.locked_players if p.team == player.team])
            if from_same_team + 1 > self.max_from_one_team:
                raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                               self.max_from_one_team)
        try:
            link_players_with_positions(self.locked_players + [player], self._settings.positions)
        except LineupOptimizerException:
            raise LineupOptimizerException('You\'re already select all %s\'s' % '/'.join(player.positions))
        self._lineup.append(player)

    def remove_player_from_lineup(self, player: Player):
        """
        Removes specified player from lineup.
        """
        try:
            self._lineup.remove(player)
        except ValueError:
            raise LineupOptimizerException('Player not in line up!')

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

    # def set_positions_for_same_team(self, *positions_stacks: List[Union[str, Tuple[str, ...]]]):
    #     warnings.simplefilter('always', DeprecationWarning)
    #     warnings.warn('set_positions_for_same_team method will be removed in 3.3, use add_stack instead', DeprecationWarning)
    #     if positions_stacks and positions_stacks[0] is not None:
    #         team_stacks = [
    #             PositionsStack(stack, max_exposure_per_team=self.teams_exposures) for stack in positions_stacks]
    #         for stack in team_stacks:
    #             self.add_stack(stack)

    def set_max_repeating_players(self, max_repeating_players: int):
        if max_repeating_players >= self.total_players:
            raise LineupOptimizerException('Maximum repeating players should be smaller than %d' % self.total_players)
        elif max_repeating_players < 1:
            raise LineupOptimizerException('Maximum repeating players should be 1 or greater')
        self.max_repeating_players = max_repeating_players
        self.add_new_rule(MaxRepeatingPlayersRule)

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

    # def set_team_stacking(self, stacks: Optional[List[int]], for_positions: Optional[List[str]] = None):
    #     warnings.simplefilter('always', DeprecationWarning)
    #     warnings.warn('set_team_stacking method will be removed in 3.3, use add_stack instead', DeprecationWarning)
    #     if stacks:
    #         team_stacks = [TeamStack(stack, for_positions=for_positions, max_exposure_per_team=self.teams_exposures) for stack in stacks]
    #         for stack in team_stacks:
    #             self.add_stack(stack)

    def restrict_positions_for_opposing_team(
            self,
            first_team_positions: List[str],
            second_team_positions: List[str],
            max_allowed: int = 0,
    ):
        if not self.games:
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
        available_positions = self.available_positions
        if any(position not in available_positions for position in positions):
            raise LineupOptimizerException('Incorrect positions. Choices are: %s' % available_positions)
        self.spacing_positions = positions
        self.spacing = spacing
        self.add_new_rule(RosterSpacingRule)

    def set_total_teams(self, total_teams: int):
        min_teams = self.settings.min_teams
        max_from_one_team = self.settings.max_from_one_team
        total_players = self.settings.get_total_players()
        if not min_teams and max_from_one_team:
            min_teams = ceil(total_players / max_from_one_team)
        if min_teams and total_teams < min_teams:
            raise LineupOptimizerException('Minimum number of teams is %d' % min_teams)
        if total_teams > total_players:
            raise LineupOptimizerException('Maximum number of teams is %d' % total_players)
        self.total_teams = total_teams

    def add_players_group(self, group: BaseGroup) -> None:
        stack = Stack(groups=[group])
        self.stacks.append(stack)

    def add_stack(self, stack: BaseStack) -> None:
        stack.validate(self)
        self.stacks.append(stack)

    def set_min_starters(self, min_starters: int) -> None:
        if min_starters > self.settings.get_total_players():
            raise LineupOptimizerException('Num of starters can\'t be greater than max players')
        if min_starters > len([p for p in self.players if p.is_confirmed_starter]):
            raise LineupOptimizerException('Num of starters can\'t be greater than max starters')
        self.min_starters = min_starters
        self.add_new_rule(MinStartersRule)

    def optimize(
            self,
            n: int,
            max_exposure: Optional[float] = None,
            randomness: bool = False,
            with_injured: bool = False,
            exposure_strategy: Type[BaseExposureStrategy] = TotalExposureStrategy,
    ) -> Generator[Lineup, None, None]:
        players = [player for player in self.players if player.max_exposure is None or player.max_exposure > 0]
        context = OptimizationContext(
            total_lineups=n,
            players=players,
            max_exposure=max_exposure,
            randomness=randomness,
            with_injured=with_injured,
            exposure_strategy=exposure_strategy,
        )
        rules = self._rules.copy()
        rules.update(self.settings.extra_rules)
        if randomness:
            rules.add(RandomObjective)
        else:
            rules.add(NormalObjective)
        if with_injured:
            rules.remove(RemoveInjuredRule)
        base_solver = self._solver_class()
        base_solver.setup_solver()
        players_dict = OrderedDict(
            [(player, base_solver.add_variable('Player_%d' % i)) for i, player in enumerate(players)])
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
                if self.total_players and len(self.locked_players) == self.total_players:
                    return
                for constraint in constraints:
                    constraint.post_optimize(variables_names)
            except SolverException:
                raise LineupOptimizerException('Can\'t generate lineups')
        self.last_context = context

    def optimize_lineups(self, lineups: List[Lineup]):
        players = [player for player in self.players if player.max_exposure is None or player.max_exposure > 0]
        context = OptimizationContext(
            total_lineups=len(lineups),
            players=players,
            existed_lineups=lineups,
        )
        rules = self._rules.copy()
        rules.update(self.settings.extra_rules)
        rules.add(NormalObjective)
        rules.add(LateSwapRule)
        rules.remove(PositionsRule)
        base_solver = self._solver_class()
        base_solver.setup_solver()
        players_dict = OrderedDict(
            [(player, base_solver.add_variable('Player_%d' % i)) for i, player in enumerate(players)])
        variables_dict = {v: k for k, v in players_dict.items()}
        constraints = [constraint(self, players_dict, context) for constraint in rules]
        for constraint in constraints:
            constraint.apply(base_solver)
        previous_lineup = None
        for lineup in lineups:
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
                context.add_lineup(lineup)
                yield generated_lineup
                if len(self.locked_players) == self.total_players:
                    return
                for constraint in constraints:
                    constraint.post_optimize(variables_names)
            except SolverException:
                raise LineupOptimizerException('Can\'t generate lineups')
        self.last_context = context

    def print_statistic(self) -> None:
        if self.last_context is None:
            raise LineupOptimizerException('You should generate lineups before printing statistic')
        Statistic(self).print_report()

    def export(self, filename: str) -> None:
        if self.last_context is None:
            raise LineupOptimizerException('You should generate lineups before printing statistic')
        self.settings.csv_exporter(self.last_context.lineups).export(filename)

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
        players_with_positions = link_players_with_positions(players, positions)
        for player, position in players_with_positions.items():
            lineup.append(LineupPlayer(player, position.name, used_fppg=context.players_used_fppg.get(player)))
        positions_order = [pos.name for pos in self._settings.positions]
        lineup.sort(key=lambda p: positions_order.index(p.lineup_position))
        return Lineup(lineup, self._settings.lineup_printer)

    def _check_team_constraint(self, team: str, num_of_players: int):
        if team not in self.available_teams:
            raise LineupOptimizerIncorrectTeamName('%s is incorrect team name. Choices are [%s]' %
                                                   (team, ','.join(self.available_teams)))
        if self.max_from_one_team and num_of_players > self.max_from_one_team:
            raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                           self.max_from_one_team)

    def _check_position_constraint(self, position: str):
        if position not in self.available_positions:
            raise LineupOptimizerIncorrectPositionName('%s is incorrect position name. Chocies are [%s]' %
                                                       (position, ','.join(self.available_positions)))

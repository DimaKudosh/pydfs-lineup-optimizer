from __future__ import division
from collections import defaultdict, Counter
from itertools import product, combinations, groupby, permutations, chain
from math import ceil
from random import getrandbits, uniform
from typing import List, Dict, DefaultDict, Set, Tuple, Any, Optional, TYPE_CHECKING, Counter as TypingCounter
from pydfs_lineup_optimizer.solvers import Solver, SolverSign
from pydfs_lineup_optimizer.utils import list_intersection, get_positions_for_optimizer, get_remaining_positions, \
    get_players_grouped_by_teams
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.player import Player


if TYPE_CHECKING:  # pragma: no cover
    from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer


class OptimizerRule(object):
    def __init__(self, optimizer, params):
        # type: ('LineupOptimizer', Dict[str, Any]) -> None
        self.params = params
        self.optimizer = optimizer

    def apply(self, solver, players_dict):
        # type: (Solver, Dict[Player, Any]) -> None
        pass

    def apply_for_iteration(self, solver, players_dict, result):
        # type: (Solver, Dict[Player, Any], Optional[Lineup]) -> None
        pass


class NormalObjective(OptimizerRule):
    def apply(self, solver, players_dict):
        variables = []
        coefficients = []
        for player, variable in players_dict.items():
            variables.append(variable)
            coefficients.append(player.fppg)
        solver.set_objective(variables, coefficients)


class RandomObjective(OptimizerRule):
    def apply_for_iteration(self, solver, players_dict, result):
        variables = []
        coefficients = []
        for player, variable in players_dict.items():
            variables.append(variable)
            coefficients.append(player.fppg * (1 + (-1 if bool(getrandbits(1)) else 1) *
                                               uniform(*self.optimizer.get_deviation())))
        solver.set_objective(variables, coefficients)


class UniqueLineupRule(OptimizerRule):
    def __init__(self, optimizer, params):
        super(UniqueLineupRule, self).__init__(optimizer, params)
        self.used_combinations = []  # type: List[Any]

    def apply_for_iteration(self, solver, players_dict, result):
        if not result:
            return
        self.used_combinations.append([players_dict[player] for player in result])
        total_players = self.optimizer.total_players
        for variables in self.used_combinations:
            solver.add_constraint(variables, None, SolverSign.LTE, total_players - 1)


class TotalPlayersRule(OptimizerRule):
    def apply(self, solver, players_dict):
        variables = players_dict.values()
        solver.add_constraint(variables, None, SolverSign.EQ, self.optimizer.total_players)


class LineupBudgetRule(OptimizerRule):
    def apply(self, solver, players_dict):
        variables = []
        coefficients = []
        for player, variable in players_dict.items():
            variables.append(variable)
            coefficients.append(player.salary)
        solver.add_constraint(variables, coefficients, SolverSign.LTE, self.optimizer.budget)


class LockedPlayersRule(OptimizerRule):
    def __init__(self, optimizer, params):
        super(LockedPlayersRule, self).__init__(optimizer, params)
        self.used_players = defaultdict(int)  # type: DefaultDict[Player, int]
        self.total_lineups = params.get('n')
        self.remaining_iteration = params.get('n') + 1

    def apply_for_iteration(self, solver, players_dict, result):
        force_variables = []
        exclude_variables = []
        self.remaining_iteration -= 1
        for player, variable in players_dict.items():
            if not player.min_exposure:
                continue
            if ceil(player.min_exposure * self.total_lineups) >= \
                    self.remaining_iteration - self.used_players.get(player, 0):
                force_variables.append(variable)
        if result:
            for player in result.lineup:
                self.used_players[player] += 1
        removed_players = []
        for player, used in self.used_players.items():
            max_exposure = player.max_exposure if player.max_exposure is not None else self.params.get('max_exposure')
            if max_exposure is not None and max_exposure <= used / self.total_lineups:
                removed_players.append(player)
                exclude_variables.append(players_dict[player])
        for player in self.optimizer.locked_players:
            if player not in removed_players:
                force_variables.append(players_dict[player])
        if force_variables:
            solver.add_constraint(force_variables, None, SolverSign.EQ, len(force_variables))
        if exclude_variables:
            solver.add_constraint(exclude_variables, None, SolverSign.EQ, 0)


class PositionsRule(OptimizerRule):
    def apply(self, solver, players_dict):
        optimizer = self.optimizer
        extra_positions = optimizer.players_with_same_position
        positions_combinations = set([tuple(sorted(player.positions)) for player in players_dict.keys()
                                      if len(player.positions) > 1])
        positions = get_positions_for_optimizer(optimizer.settings.positions, positions_combinations)
        unique_positions = optimizer.available_positions
        players_by_positions = {
            position: {variable for player, variable in players_dict.items()
                       if position in player.positions} for position in unique_positions
        }
        for position, places in positions.items():
            extra = 0
            if len(position) == 1:
                extra = extra_positions.get(position[0], 0)
            players_with_position = set()
            for pos in position:
                players_with_position.update(players_by_positions[pos])
            solver.add_constraint(players_with_position, None, SolverSign.GTE, places + extra)


class TeamMatesRule(OptimizerRule):
    def apply(self, solver, players_dict):
        for team, quantity in self.optimizer.players_from_one_team.items():
            players_from_same_team = [variable for player, variable in players_dict.items() if player.team == team]
            solver.add_constraint(players_from_same_team, None, SolverSign.EQ, quantity)


class MaxFromOneTeamRule(OptimizerRule):
    def apply(self, solver, players_dict):
        if not self.optimizer.max_from_one_team:
            return
        for team in self.optimizer.available_teams:
            players_from_team = [variable for player, variable in players_dict.items() if player.team == team]
            solver.add_constraint(players_from_team, None, SolverSign.LTE, self.optimizer.max_from_one_team)


class MinSalaryCapRule(OptimizerRule):
    def apply(self, solver, players_dict):
        variables = []
        coefficients = []
        for player, variable in players_dict.items():
            variables.append(variable)
            coefficients.append(player.salary)
        min_salary_cap = self.optimizer.min_salary_cap
        solver.add_constraint(variables, coefficients, SolverSign.GTE, min_salary_cap)


class FromSameTeamByPositionsRule(OptimizerRule):
    def __init__(self, optimizer, params):
        super(FromSameTeamByPositionsRule, self).__init__(optimizer, params)
        self.stacks_dict = Counter(
            map(tuple, self.optimizer.positions_stacks_from_same_team)
        )  # type: TypingCounter[Tuple[str, ...]]
        self.used_teams = defaultdict(int)  # type: DefaultDict[str, int]
        self.total_lineups = params.get('n')
        self.teams_max_exposures = optimizer.teams_exposures
        self.players_combinations_by_team = {}  # type: Dict[Tuple[str, ...], Dict[str, Set]]

    def apply(self, solver, players_dict):
        self.players_combinations_by_team = self._get_players_combinations_by_team(players_dict)
        if not self.teams_max_exposures:
            self._create_constraints(solver)

    def apply_for_iteration(self, solver, players_dict, result):
        if not self.teams_max_exposures:
            return
        if not result:
            self._create_constraints(solver)
            return
        for team in self._detect_teams_used_in_stacks(result):
            self.used_teams[team] += 1
        # Get teams reached max exposure
        exclude_teams = set()
        for team, max_exposure in self.teams_max_exposures.items():
            if max_exposure is not None and max_exposure <= self.used_teams[team] / self.total_lineups:
                exclude_teams.add(team)
        self._create_constraints(solver, exclude_teams)

    def _get_players_combinations_by_team(self, players_dict):
        players_combinations_by_team = defaultdict(
            lambda: defaultdict(set)
        )  # type: Dict[Tuple[str, ...], Dict[str, Set]]
        players_by_teams = get_players_grouped_by_teams(players_dict.keys())
        for stack in self.stacks_dict.keys():
            for team_name, team_players in players_by_teams.items():
                all_players_combinations = set()
                players_by_positions = []
                for position in stack:
                    players_by_positions.append([player for player in team_players if position in player.positions])
                # Create all possible players combinations for stack
                for players_combination in product(*players_by_positions):
                    # Remove combinations with duplicated players
                    if len(set(players_combination)) != len(stack):
                        continue
                    players_combination = tuple([
                        players_dict[player] for player in sorted(players_combination, key=lambda p: p.id)
                    ])
                    all_players_combinations.add(players_combination)
                players_combinations_by_team[stack][team_name] = all_players_combinations
        return players_combinations_by_team

    def _create_constraints(self, solver, exclude_teams=None):
        combination_variables_by_team = defaultdict(list)  # type: Dict[str, List]
        for stack, total_stacks in self.stacks_dict.items():
            stack_variables = []
            variable_prefix = 'rules_%s' % '_'.join(stack)
            for team_name, variables in self.players_combinations_by_team[stack].items():
                if exclude_teams and team_name in exclude_teams:
                    for combination_variables in variables:
                        solver.add_constraint(combination_variables, None, SolverSign.LTE, len(stack) - 1)
                    continue
                for combination_variables in variables:
                    variable_name = '%s_players_%s_%s' % (variable_prefix, team_name,
                                                          '_'.join([str(v) for v in combination_variables]))
                    variable = solver.add_variable(variable_name)
                    combination_variables_by_team[team_name].append(variable)
                    stack_variables.append(variable)
                    solver.add_constraint(combination_variables, None, SolverSign.GTE, len(stack) * variable)
            solver.add_constraint(stack_variables, None, SolverSign.GTE, total_stacks)
        for combination_variables in combination_variables_by_team.values():
            solver.add_constraint(combination_variables, None, SolverSign.LTE, 1)

    def _detect_teams_used_in_stacks(self, lineup):
        teams = set([player.team for player in lineup])
        all_teams_used_in_stacks = set()
        for stack in self.stacks_dict.keys():
            teams_used_in_stack = teams.copy()
            for position in stack:
                teams_used_in_stack = teams_used_in_stack.intersection(
                    set([player.team for player in lineup if position in player.positions])
                )
            all_teams_used_in_stacks.update(teams_used_in_stack)
        return all_teams_used_in_stacks


class RemoveInjuredRule(OptimizerRule):
    def apply(self, solver, players_dict):
        injured_players_variables = [variable for player, variable in players_dict.items() if player.is_injured]
        solver.add_constraint(injured_players_variables, None, SolverSign.EQ, 0)


class MaxRepeatingPlayersRule(OptimizerRule):
    def __init__(self, optimizer, params):
        super(MaxRepeatingPlayersRule, self).__init__(optimizer, params)
        self.exclude_combinations = []  # type: List[Any]

    def apply_for_iteration(self, solver, players_dict, result):
        max_repeating_players = self.optimizer.max_repeating_players
        if max_repeating_players is None or not result:
            return
        self.exclude_combinations.append([players_dict[player] for player in result])
        for players_combination in self.exclude_combinations:
            solver.add_constraint(players_combination, None, SolverSign.LTE, max_repeating_players)


class ProjectedOwnershipRule(OptimizerRule):
    def apply(self, solver, players_dict):
        min_variables = []
        min_coefficients = []
        max_variables = []
        max_coefficients = []
        min_projected_ownership = self.optimizer.min_projected_ownership
        max_projected_ownership = self.optimizer.max_projected_ownership
        for player, variable in players_dict.items():
            if player.projected_ownership is None:
                continue
            if min_projected_ownership:
                min_variables.append(variable)
                min_coefficients.append(player.projected_ownership - min_projected_ownership)
            if max_projected_ownership:
                max_variables.append(variable)
                max_coefficients.append(player.projected_ownership - max_projected_ownership)
        if min_variables:
            solver.add_constraint(min_variables, min_coefficients, SolverSign.GTE, 0)
        if max_variables:
            solver.add_constraint(max_variables, max_coefficients, SolverSign.LTE, 0)


class UniquePlayerRule(OptimizerRule):
    @staticmethod
    def sort_players(player_tuple):
        return player_tuple[0].full_name

    def apply(self, solver, players_dict):
        data = sorted(players_dict.items(), key=self.sort_players)
        for player_id, group_iterator in groupby(data, key=self.sort_players):
            group = list(group_iterator)
            if len(group) == 1:
                continue
            variables = [variable for player, variable in group]
            solver.add_constraint(variables, None, SolverSign.LTE, 1)


class LateSwapRule(OptimizerRule):
    def __init__(self, optimizer, params):
        super(LateSwapRule, self).__init__(optimizer, params)
        self.current_iteration = 0
        self.lineups = params.get('lineups')  # type: List[Lineup]

    def apply_for_iteration(self, solver, players_dict, result):
        current_lineup = self.lineups[self.current_iteration]
        unswappable_players = current_lineup.get_unswappable_players()
        remaining_positions = get_remaining_positions(self.optimizer.settings.positions, unswappable_players)
        # lock selected players
        for player in unswappable_players:
            solver.add_constraint([players_dict[player]], None, SolverSign.EQ, 1)
        # set remaining positions
        positions_combinations = set([tuple(sorted(player.positions)) for player in players_dict.keys()
                                      if len(player.positions) > 1])
        positions = get_positions_for_optimizer(remaining_positions, positions_combinations)
        players_for_optimization = set()
        for position, places in positions.items():
            players_with_position = [variable for player, variable in players_dict.items()
                                     if list_intersection(position, player.positions) and
                                     player not in unswappable_players]
            players_for_optimization.update(players_with_position)
            solver.add_constraint(players_with_position, None, SolverSign.GTE, places)
        # Set total players for optimization
        solver.add_constraint(players_for_optimization, None, SolverSign.EQ, len(remaining_positions))
        # Exclude players with active games
        for player, variable in players_dict.items():
            if player not in unswappable_players and player.is_game_started:
                solver.add_constraint([players_dict[player]], None, SolverSign.EQ, 0)
        self.current_iteration += 1


class TeamStacksRule(OptimizerRule):
    def __init__(self, optimizer, params):
        super(TeamStacksRule, self).__init__(optimizer, params)
        stacks = self.optimizer.team_stacks
        self.stacks_dict = {}  # type: Dict[int, int]
        for i, stack in enumerate(sorted(stacks, reverse=True), start=1):
            self.stacks_dict[stack] = i
        self.used_teams = defaultdict(int)  # type: Dict[str, int]
        self.total_lineups = params.get('n')
        self.teams_max_exposures = optimizer.teams_exposures
        self.min_count_not_in_stack = max(min(stacks) - 1, 1)
        remaining_slots = optimizer.settings.get_total_players() - sum(stacks)
        self.add_exclude_constraints = remaining_slots > self.min_count_not_in_stack
        self.player_variables_by_teams = {}  # type: Dict[str, List]

    def apply(self, solver, players_dict):
        all_players = players_dict.keys()
        for_positions = self.optimizer.team_stacks_for_positions
        if for_positions:
            all_players = [player for player in all_players if list_intersection(player.positions, for_positions)]
        players_by_teams = get_players_grouped_by_teams(all_players)
        for team, players in players_by_teams.items():
            variables = [players_dict[player] for player in players]
            self.player_variables_by_teams[team] = variables
        if not self.teams_max_exposures:
            self._create_constraints(solver)

    def apply_for_iteration(self, solver, players_dict, result):
        if not self.teams_max_exposures:
            return
        if not result:
            self._create_constraints(solver)
            return
        # Detect teams used in stack
        for team, total_players in Counter(player.team for player in result).most_common():
            if total_players not in self.stacks_dict:
                break
            self.used_teams[team] += 1
        # Get teams reached max exposure
        exclude_teams = set()
        for team, max_exposure in self.teams_max_exposures.items():
            if max_exposure is not None and max_exposure <= self.used_teams[team] / self.total_lineups:
                exclude_teams.add(team)
        self._create_constraints(solver, exclude_teams)
        if self.add_exclude_constraints:
            for team in exclude_teams:
                variables = self.player_variables_by_teams[team]
                solver.add_constraint(variables, None, SolverSign.LTE, self.min_count_not_in_stack)

    def _create_constraints(self, solver, exclude_teams=None):
        for stack, total in self.stacks_dict.items():
            combinations_variables = []
            for team, variables in self.player_variables_by_teams.items():
                if exclude_teams and team in exclude_teams:
                    continue
                solver_variable = solver.add_variable('teams_stack_%d_%s' % (stack, team))
                combinations_variables.append(solver_variable)
                solver.add_constraint(variables, None, SolverSign.GTE, stack * solver_variable)
            solver.add_constraint(combinations_variables, None, SolverSign.GTE, total)


class RestrictPositionsForOpposingTeams(OptimizerRule):
    def apply(self, solver, players_dict):
        if not self.optimizer.opposing_teams_position_restriction:
            return
        for game in self.optimizer.games:
            first_team_players = {player: variable for player, variable in players_dict.items()
                                  if player.team == game.home_team}
            second_team_players = {player: variable for player, variable in players_dict.items()
                                   if player.team == game.away_team}
            for first_team_positions, second_team_positions in \
                    permutations(self.optimizer.opposing_teams_position_restriction, 2):
                first_team_variables = [variable for player, variable in first_team_players.items()
                                        if list_intersection(player.positions, first_team_positions)]
                second_team_variables = [variable for player, variable in second_team_players.items()
                                         if list_intersection(player.positions, second_team_positions)]
                for variables in product(first_team_variables, second_team_variables):
                    solver.add_constraint(variables, None, SolverSign.LTE, 1)


class RosterSpacingRule(OptimizerRule):
    @staticmethod
    def sort_players(player_tuple):
        return player_tuple[0].roster_order

    def apply(self, solver, players_dict):
        optimizer = self.optimizer
        positions, spacing = optimizer.spacing_positions, optimizer.spacing
        if not spacing or not positions:
            return
        available_players = sorted([
                (player, variable) for player, variable in players_dict.items()
                if player.roster_order is not None and list_intersection(player.positions, positions)
            ],
            key=self.sort_players,
        )
        players_by_roster_positions = {players_spacing: list(players) for players_spacing, players in
                                       groupby(available_players, key=self.sort_players)}
        for roster_position, players in players_by_roster_positions.items():
            next_restricted_roster_position = roster_position + spacing
            restricted_players = chain.from_iterable(
                players for players_spacing, players in players_by_roster_positions.items()
                if players_spacing >= next_restricted_roster_position
            )
            for first_player, first_variable in restricted_players:
                for second_player, second_variable in players:
                    if first_player.team != second_player.team:
                        continue
                    solver.add_constraint([first_variable, second_variable], None, SolverSign.LTE, 1)


class FanduelBaseballRosterRule(OptimizerRule):
    HITTERS = ('1B', '2B', '3B', 'SS', 'C', 'OF')
    MAXIMUM_HITTERS_FROM_ONE_TEAM = 4

    def apply(self, solver, players_dict):
        players_dict = {player: variable for player, variable in players_dict.items() if
                        list_intersection(player.positions, self.HITTERS)}
        for team in self.optimizer.available_teams:
            players_from_team = [variable for player, variable in players_dict.items() if player.team == team]
            solver.add_constraint(players_from_team, None, SolverSign.LTE, self.MAXIMUM_HITTERS_FROM_ONE_TEAM)


class FanduelMinimumTeamsRule(OptimizerRule):
    MINIMUM_TEAMS = 3

    def apply(self, solver, players_dict):
        for teams in combinations(self.optimizer.available_teams, self.MINIMUM_TEAMS - 1):
            players_from_teams = [variable for player, variable in players_dict.items() if player.team in teams]
            solver.add_constraint(players_from_teams, None, SolverSign.LTE,
                                  self.optimizer.settings.get_total_players() - 1)

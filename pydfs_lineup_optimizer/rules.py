from uuid import uuid4
from math import ceil
from collections import defaultdict, Counter
from itertools import product, groupby, permutations, chain
from random import getrandbits, uniform
from typing import List, Dict, DefaultDict, Set, Tuple, Any, Optional, TYPE_CHECKING
from pydfs_lineup_optimizer.solvers import Solver, SolverSign
from pydfs_lineup_optimizer.utils import list_intersection, get_positions_for_optimizer, get_remaining_positions, \
    get_players_grouped_by_teams
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.context import OptimizationContext


if TYPE_CHECKING:  # pragma: no cover
    from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
    from pydfs_lineup_optimizer.stacks import BaseGroup


__all__ = [
    'OptimizerRule', 'NormalObjective', 'RandomObjective', 'UniqueLineupRule', 'TotalPlayersRule',
    'LineupBudgetRule', 'LockedPlayersRule', 'PositionsRule', 'TeamMatesRule', 'MaxFromOneTeamRule',
    'MinSalaryCapRule', 'RemoveInjuredRule', 'MaxRepeatingPlayersRule',
    'ProjectedOwnershipRule', 'UniquePlayerRule', 'LateSwapRule',
    'RestrictPositionsForOpposingTeam', 'RosterSpacingRule', 'FanduelBaseballRosterRule',
    'TotalTeamsRule', 'FanduelSingleGameMaxQBRule',
    'RestrictPositionsForSameTeamRule', 'ForcePositionsForOpposingTeamRule', 'GenericStacksRule',
    'MinStartersRule', 'MinExposureRule', 'MinGamesRule', 'DraftKingsBaseballRosterRule',
    'DraftKingsTiersRule',
]


class OptimizerRule:
    def __init__(self, optimizer: 'LineupOptimizer', players_dict: Dict[Player, Any], context: OptimizationContext):
        self.optimizer = optimizer
        self.context = context
        self.players_dict = players_dict

    def apply(self, solver: Solver):
        pass

    def apply_for_iteration(self, solver: Solver, result: Optional[Lineup]):
        pass

    def post_optimize(self, solved_variables: List[str]):
        pass


class NormalObjective(OptimizerRule):
    def apply(self, solver):
        variables = []
        coefficients = []
        for player, variable in self.players_dict.items():
            variables.append(variable)
            coefficients.append(player.fppg)
        solver.set_objective(variables, coefficients)


class RandomObjective(OptimizerRule):
    def apply_for_iteration(self, solver, result):
        variables = []
        coefficients = []
        optimizer_min_deviation, optimizer_max_deviation = self.optimizer.get_deviation()
        for player, variable in self.players_dict.items():
            variables.append(variable)
            if player.fppg_floor is not None and player.fppg_ceil is not None:
                random_fppg = uniform(player.fppg_floor, player.fppg_ceil)
            else:
                multiplier = uniform(
                    player.min_deviation if player.min_deviation is not None else optimizer_min_deviation,
                    player.max_deviation if player.max_deviation is not None else optimizer_max_deviation
                )
                random_fppg = player.fppg * (1 + (-1 if bool(getrandbits(1)) else 1) * multiplier)
            self.context.players_used_fppg[player] = random_fppg
            coefficients.append(random_fppg)
        solver.set_objective(variables, coefficients)


class UniqueLineupRule(OptimizerRule):
    def __init__(self, optimizer, players_dict, context):
        super().__init__(optimizer, players_dict, context)
        self.used_combinations = []  # type: List[Any]

    def apply_for_iteration(self, solver, result):
        if not result:
            return
        self.used_combinations.append([self.players_dict[player] for player in result])
        total_players = self.optimizer.total_players or len(self.used_combinations[0])
        for variables in self.used_combinations:
            solver.add_constraint(variables, None, SolverSign.LTE, total_players - 1)


class TotalPlayersRule(OptimizerRule):
    def apply(self, solver):
        if self.optimizer.total_players:
            variables = self.players_dict.values()
            solver.add_constraint(variables, None, SolverSign.EQ, self.optimizer.total_players)


class LineupBudgetRule(OptimizerRule):
    def apply(self, solver):
        if not self.optimizer.budget:
            return
        variables = []
        coefficients = []
        for player, variable in self.players_dict.items():
            variables.append(variable)
            coefficients.append(player.salary)
        solver.add_constraint(variables, coefficients, SolverSign.LTE, self.optimizer.budget)


class LockedPlayersRule(OptimizerRule):
    def __init__(self, optimizer, players_dict, context):
        super().__init__(optimizer, players_dict, context)
        exposures = {}
        for player, variable in players_dict.items():
            exposures[variable.name] = player.max_exposure if player.max_exposure is not None \
                else self.context.max_exposure
        self.max_exposure_strategy = context.exposure_strategy(
            exposures, self.context.total_lineups)

    def apply_for_iteration(self, solver, result):
        force_variables = []
        exclude_variables = []
        removed_players = []
        for player, variable in self.players_dict.items():
            if not self.max_exposure_strategy.is_reached_exposure(variable.name):
                continue
            removed_players.append(player)
            exclude_variables.append(variable)
        for player in self.optimizer.locked_players:
            if player not in removed_players:
                force_variables.append(self.players_dict[player])
        if force_variables:
            solver.add_constraint(force_variables, None, SolverSign.EQ, len(force_variables))
        if exclude_variables:
            solver.add_constraint(exclude_variables, None, SolverSign.EQ, 0)

    def post_optimize(self, solved_variables: List[str]):
        self.max_exposure_strategy.set_used(solved_variables)


class PositionsRule(OptimizerRule):
    def apply(self, solver):
        optimizer = self.optimizer
        if not optimizer.available_positions:
            return
        extra_positions = optimizer.players_with_same_position
        positions_combinations = set([tuple(sorted(player.positions)) for player in self.players_dict.keys()
                                      if len(player.positions) > 1])
        positions = get_positions_for_optimizer(optimizer.settings.positions, positions_combinations)
        unique_positions = optimizer.available_positions
        players_by_positions = {
            position: {variable for player, variable in self.players_dict.items()
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
    def apply(self, solver):
        for team, quantity in self.optimizer.players_from_one_team.items():
            players_from_same_team = [variable for player, variable in self.players_dict.items() if player.team == team]
            solver.add_constraint(players_from_same_team, None, SolverSign.EQ, quantity)


class MaxFromOneTeamRule(OptimizerRule):
    def apply(self, solver):
        if not self.optimizer.max_from_one_team:
            return
        for team in self.optimizer.available_teams:
            players_from_team = [variable for player, variable in self.players_dict.items() if player.team == team]
            solver.add_constraint(players_from_team, None, SolverSign.LTE, self.optimizer.max_from_one_team)


class MinSalaryCapRule(OptimizerRule):
    def apply(self, solver):
        variables = []
        coefficients = []
        for player, variable in self.players_dict.items():
            variables.append(variable)
            coefficients.append(player.salary)
        min_salary_cap = self.optimizer.min_salary_cap
        solver.add_constraint(variables, coefficients, SolverSign.GTE, min_salary_cap)


class RemoveInjuredRule(OptimizerRule):
    def apply(self, solver):
        injured_players_variables = [variable for player, variable in self.players_dict.items() if player.is_injured]
        solver.add_constraint(injured_players_variables, None, SolverSign.EQ, 0)


class MaxRepeatingPlayersRule(OptimizerRule):
    def __init__(self, optimizer, players_dict, context):
        super().__init__(optimizer, players_dict, context)
        self.exclude_combinations = []  # type: List[Any]

    def apply_for_iteration(self, solver, result):
        max_repeating_players = self.optimizer.max_repeating_players
        if max_repeating_players is None or not result:
            return
        self.exclude_combinations.append([self.players_dict[player] for player in result])
        for players_combination in self.exclude_combinations:
            solver.add_constraint(players_combination, None, SolverSign.LTE, max_repeating_players)


class ProjectedOwnershipRule(OptimizerRule):
    def apply(self, solver):
        min_variables = []
        min_coefficients = []
        max_variables = []
        max_coefficients = []
        min_projected_ownership = self.optimizer.min_projected_ownership
        max_projected_ownership = self.optimizer.max_projected_ownership
        for player, variable in self.players_dict.items():
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

    def apply(self, solver):
        data = sorted(self.players_dict.items(), key=self.sort_players)
        for player_id, group_iterator in groupby(data, key=self.sort_players):
            group = list(group_iterator)
            if len(group) == 1:
                continue
            variables = [variable for player, variable in group]
            solver.add_constraint(variables, None, SolverSign.LTE, 1)


class LateSwapRule(OptimizerRule):
    def __init__(self, optimizer, players_dict, context):
        super().__init__(optimizer, players_dict, context)
        self.current_iteration = 0
        self.lineups = context.existed_lineups

    def apply_for_iteration(self, solver, result):
        current_lineup = self.lineups[self.current_iteration]
        unswappable_players = current_lineup.get_unswappable_players()
        remaining_positions = get_remaining_positions(self.optimizer.settings.positions, unswappable_players)
        # lock selected players
        for player in unswappable_players:
            solver.add_constraint([self.players_dict[player]], None, SolverSign.EQ, 1)
        # set remaining positions
        positions_combinations = set([tuple(sorted(player.positions)) for player in self.players_dict.keys()
                                      if len(player.positions) > 1])
        positions = get_positions_for_optimizer(remaining_positions, positions_combinations)
        players_for_optimization = set()
        for position, places in positions.items():
            players_with_position = [variable for player, variable in self.players_dict.items()
                                     if list_intersection(position, player.positions) and
                                     player not in unswappable_players]
            players_for_optimization.update(players_with_position)
            solver.add_constraint(players_with_position, None, SolverSign.GTE, places)
        # Set total players for optimization
        solver.add_constraint(players_for_optimization, None, SolverSign.EQ, len(remaining_positions))
        # Exclude players with active games
        for player, variable in self.players_dict.items():
            if player not in unswappable_players and player.is_game_started:
                solver.add_constraint([self.players_dict[player]], None, SolverSign.EQ, 0)
        self.current_iteration += 1


class GenericStacksRule(OptimizerRule):
    def __init__(self, optimizer, players_dict, context):
        super().__init__(optimizer, players_dict, context)
        self.stacks = list(chain.from_iterable(stack.build_stacks(context.players, optimizer)
                                               for stack in optimizer.stacks))
        self.with_exposures = any(stack.with_exposures for stack in self.stacks)
        exposures = {}
        for stack in self.stacks:
            for group in stack.groups:
                if group.max_exposure is None:
                    continue
                exposures[self._build_group_name(group)] = group.max_exposure
        self.exposure_strategy = context.exposure_strategy(
            exposures, self.context.total_lineups)

    def apply(self, solver):
        if not self.with_exposures:
            self._create_constraints(solver)

    def apply_for_iteration(self, solver, result):
        if self.with_exposures:
            self._create_constraints(solver)

    @staticmethod
    def _build_group_name(group: 'BaseGroup'):
        return 'stack_%s' % group.uuid.hex

    def _create_constraints(self, solver: Solver,):
        players_in_stack = defaultdict(set)  # type: Dict[Player, Set[Any]]
        for stack in self.stacks:
            combinations_variables = {}
            for group in stack.groups:
                group_name = self._build_group_name(group)
                sub_groups = group.get_all_players_groups()
                if self.exposure_strategy.is_reached_exposure(group_name) or \
                        (group.parent and self.exposure_strategy.is_reached_exposure(
                            self._build_group_name(group.parent))):
                    for group_players, _, max_from_group in sub_groups:
                        if max_from_group is None:
                            continue
                        solver.add_constraint([self.players_dict[p] for p in group_players], None, SolverSign.EQ, 0)
                    max_group = sorted(sub_groups, key=lambda t: t[1])[0]
                    if max_group[1]:
                        solver.add_constraint([self.players_dict[p] for p in max_group[0]], None, SolverSign.LTE,
                                              max_group[1] - 1)
                    continue
                solver_variable = None
                if any(sub_group[1] is not None for sub_group in sub_groups):
                    solver_variable = solver.add_variable(group_name)
                    combinations_variables[group_name] = solver_variable
                for group_players, group_min, group_max in sub_groups:
                    variables = [self.players_dict[p] for p in group_players]
                    if group_min is not None:
                        if not stack.can_intersect:
                            for player in group_players:
                                players_in_stack[player].add(solver_variable)
                        solver.add_constraint(variables, None, SolverSign.GTE, group_min * solver_variable)
                        if group_max is not None:
                            solver.add_constraint(variables, None, SolverSign.LTE, group_max)
                    elif group_max is not None:
                        solver_variable = solver.add_variable(group_name, min_value=0, max_value=group_max)
                        solver.add_constraint(variables, None, SolverSign.EQ, solver_variable)
            if combinations_variables:
                solver.add_constraint(combinations_variables.values(), None, SolverSign.GTE, 1)
        for player, stacks_vars in players_in_stack.items():
            if len(stacks_vars) > 1:
                solver.add_constraint(stacks_vars, None, SolverSign.LTE, 1)

    def post_optimize(self, solved_variables):
        self.exposure_strategy.set_used(solved_variables)


class MinExposureRule(OptimizerRule):
    def __init__(self, optimizer, players_dict, context):
        super().__init__(optimizer, players_dict, context)
        self.min_exposure_players = {
            player: round(player.min_exposure * context.total_lineups)
            for player in context.players if player.min_exposure
        }
        self.positions = {}
        if self.min_exposure_players:
            self.positions = get_positions_for_optimizer(optimizer.settings.positions, None)

    def apply_for_iteration(self, solver, result):
        if not self.min_exposure_players:
            return
        if result:
            for player in result:
                if player not in self.min_exposure_players:
                    continue
                self.min_exposure_players[player] -= 1
                if self.min_exposure_players[player] == 0:
                    del self.min_exposure_players[player]
        self._create_constraints(solver)

    def _create_constraints(self, solver: Solver) -> None:
        remaining_lineups = self.context.remaining_lineups
        for positions, total_for_positions in self.positions.items():
            min_exposure_players = [p for p in self.min_exposure_players if list_intersection(p.positions, positions)]
            if not min_exposure_players:
                continue
            total_force = sum(self.min_exposure_players[p] for p in min_exposure_players) - \
                          total_for_positions * (remaining_lineups - 1)
            if total_force > 0:
                variables = [self.players_dict[p] for p in min_exposure_players]
                total_force = min(total_force, ceil(total_force / remaining_lineups))
                solver.add_constraint(variables, None, SolverSign.GTE, total_force)
        for player, total_lineups in self.min_exposure_players.items():
            if total_lineups >= remaining_lineups:
                solver.add_constraint([self.players_dict[player]], None, SolverSign.EQ, 1)


class RestrictPositionsForOpposingTeam(OptimizerRule):
    MULTIPLIER = 1000

    def apply(self, solver):
        if not self.optimizer.opposing_teams_position_restriction:
            return
        for game in self.optimizer.games:
            home_team_players = {player: variable for player, variable in self.players_dict.items()
                                  if player.team == game.home_team}
            away_team_players = {player: variable for player, variable in self.players_dict.items()
                                   if player.team == game.away_team}
            first_team_positions, second_team_positions = self.optimizer.opposing_teams_position_restriction
            for first_team_players, second_team_players in permutations([home_team_players, away_team_players], 2):
                first_team_variables = [variable for player, variable in first_team_players.items()
                                        if list_intersection(player.positions, first_team_positions)]
                second_team_variables = [variable for player, variable in second_team_players.items()
                                         if list_intersection(player.positions, second_team_positions)]
                aggregated_var = solver.add_variable(str(uuid4()), min_value=0, max_value=len(second_team_variables))
                solver.add_constraint(second_team_variables, None, SolverSign.EQ, aggregated_var)
                for var in first_team_variables:
                    solver.add_constraint([var, aggregated_var], [self.MULTIPLIER, 1],
                                          SolverSign.LTE, self.MULTIPLIER + self.optimizer.opposing_teams_max_allowed)


class RestrictPositionsForSameTeamRule(OptimizerRule):
    def apply(self, solver):
        all_restrict_positions = self.optimizer.same_team_restrict_positions
        if not all_restrict_positions:
            return
        players_by_team = get_players_grouped_by_teams(self.players_dict.keys())
        for restrict_positions in all_restrict_positions:
            for team_players in players_by_team.values():
                first_position_players = [player for player in team_players
                                          if restrict_positions[0] in player.positions]
                second_position_players = [player for player in team_players
                                           if restrict_positions[1] in player.positions]
                for players_combination in product(first_position_players, second_position_players):
                    if players_combination[0] == players_combination[1]:
                        continue
                    variables = [self.players_dict[player] for player in players_combination]
                    solver.add_constraint(variables, None, SolverSign.LTE, 1)


class ForcePositionsForOpposingTeamRule(OptimizerRule):
    def apply(self, solver):
        raw_all_force_positions = self.optimizer.opposing_team_force_positions
        if not raw_all_force_positions:
            return
        all_force_positions = [tuple(sorted(positions)) for positions in raw_all_force_positions]
        for positions, total_combinations in Counter(all_force_positions).items():
            positions_vars = []
            combinations_count = 0
            for game in self.optimizer.games:
                first_team_players = {player: variable for player, variable in self.players_dict.items()
                                      if player.team == game.home_team}
                second_team_players = {player: variable for player, variable in self.players_dict.items()
                                       if player.team == game.away_team}
                for first_team_positions, second_team_positions in permutations(positions, 2):
                    first_team_variables = [variable for player, variable in first_team_players.items()
                                            if first_team_positions in player.positions]
                    second_team_variables = [variable for player, variable in second_team_players.items()
                                             if second_team_positions in player.positions]
                    for variables in product(first_team_variables, second_team_variables):
                        solver_variable = solver.add_variable('force_positions_%s_%d' % (positions, combinations_count))
                        combinations_count += 1
                        positions_vars.append(solver_variable)
                        solver.add_constraint(variables, None, SolverSign.GTE, 2 * solver_variable)
            solver.add_constraint(positions_vars, None, SolverSign.GTE, total_combinations)


class RosterSpacingRule(OptimizerRule):
    def apply(self, solver):
        optimizer = self.optimizer
        positions, spacing = optimizer.spacing_positions, optimizer.spacing
        if not spacing or not positions:
            return
        players_by_roster_positions = defaultdict(list)  # type: Dict[int, List[Tuple[Player, Any]]]
        for player, variable in self.players_dict.items():
            if player.roster_order is None or not list_intersection(player.positions, positions):
                continue
            players_by_roster_positions[player.roster_order].append((player, variable))
        max_order = max(players_by_roster_positions.keys())
        for roster_position, players in players_by_roster_positions.items():
            restricted_players = chain.from_iterable(
                players for players_spacing, players in players_by_roster_positions.items()
                if max_order - spacing + roster_position >= players_spacing >= roster_position + spacing
            )
            for first_player, first_variable in restricted_players:
                for second_player, second_variable in players:
                    if first_player.team != second_player.team:
                        continue
                    solver.add_constraint([first_variable, second_variable], None, SolverSign.LTE, 1)


class FanduelBaseballRosterRule(OptimizerRule):
    HITTERS = ('1B', '2B', '3B', 'SS', 'C', 'OF')
    MAXIMUM_HITTERS_FROM_ONE_TEAM = 4

    def apply(self, solver):
        players_dict = {player: variable for player, variable in self.players_dict.items() if
                        list_intersection(player.positions, self.HITTERS)}
        for team in self.optimizer.available_teams:
            players_from_team = [variable for player, variable in players_dict.items() if player.team == team]
            solver.add_constraint(players_from_team, None, SolverSign.LTE, self.MAXIMUM_HITTERS_FROM_ONE_TEAM)


class TotalTeamsRule(OptimizerRule):
    def apply(self, solver):
        total_teams = self.optimizer.total_teams
        settings = self.optimizer.settings
        min_teams = settings.min_teams
        if not min_teams and not total_teams:
            return
        total_players = self.optimizer.settings.get_total_players()
        players_by_teams = get_players_grouped_by_teams(self.players_dict.keys(), for_positions=[
            position for position in self.optimizer.available_positions
            if position not in settings.total_teams_exclude_positions
        ])
        teams_variables = []
        for team, team_players in players_by_teams.items():
            variable = solver.add_variable('total_teams_%s' % team)
            teams_variables.append(variable)
            variables = [self.players_dict[player] for player in team_players]
            solver.add_constraint(variables, None, SolverSign.LTE, variable * total_players)
            solver.add_constraint(variables, None, SolverSign.GTE, variable)
        if total_teams:
            solver.add_constraint(teams_variables, None, SolverSign.EQ, total_teams)
        else:
            solver.add_constraint(teams_variables, None, SolverSign.GTE, min_teams)


class FanduelSingleGameMaxQBRule(OptimizerRule):
    def apply(self, solver):
        variables = [var for player, var in self.players_dict.items() if 'QB' in player.original_positions]
        solver.add_constraint(variables, None, SolverSign.LTE, 2)


class MinStartersRule(OptimizerRule):
    def apply(self, solver):
        min_starters = self.optimizer.min_starters
        if not min_starters:
            return
        variables = [variable for player, variable in self.players_dict.items() if player.is_confirmed_starter]
        solver.add_constraint(variables, None, SolverSign.GTE, min_starters)


class MinGamesRule(OptimizerRule):
    def apply(self, solver):
        min_games = self.optimizer.settings.min_games
        if not min_games:
            return
        total_players = self.optimizer.settings.get_total_players() or 100
        players_by_games = defaultdict(list)
        for player in self.optimizer.players:
            if player.game_info:
                players_by_games[player.game_info].append(player)
        game_variables = []
        for game, game_players in players_by_games.items():
            variable = solver.add_variable('total_game_%s_%s' % (game.home_team, game.away_team))
            game_variables.append(variable)
            variables = [self.players_dict[player] for player in game_players]
            solver.add_constraint(variables, None, SolverSign.LTE, variable * total_players)
            solver.add_constraint(variables, None, SolverSign.GTE, variable)
        if len(game_variables) >= min_games:
            solver.add_constraint(game_variables, None, SolverSign.GTE, min_games)


class DraftKingsBaseballRosterRule(OptimizerRule):
    HITTERS = ('1B', '2B', '3B', 'SS', 'C', 'OF')
    MAXIMUM_HITTERS_FROM_ONE_TEAM = 5

    def apply(self, solver):
        players_dict = {player: variable for player, variable in self.players_dict.items() if
                        list_intersection(player.positions, self.HITTERS)}
        for team in self.optimizer.available_teams:
            players_from_team = [variable for player, variable in players_dict.items() if player.team == team]
            solver.add_constraint(players_from_team, None, SolverSign.LTE, self.MAXIMUM_HITTERS_FROM_ONE_TEAM)


class DraftKingsTiersRule(OptimizerRule):
    @staticmethod
    def sort_player(player):
        return player.positions[0]

    def apply(self, solver):
        for tier, players in groupby(sorted(self.players_dict.keys(), key=self.sort_player), key=self.sort_player):
            variables = [self.players_dict[player] for player in players]
            solver.add_constraint(variables, None, SolverSign.EQ, 1)

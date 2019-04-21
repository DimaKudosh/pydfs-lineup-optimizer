from __future__ import division
from collections import defaultdict
from itertools import product, combinations, groupby, permutations
from math import ceil
from random import getrandbits, uniform
from typing import List, Dict, DefaultDict, Any, Optional, TYPE_CHECKING
from pydfs_lineup_optimizer.solvers import Solver, SolverSign
from pydfs_lineup_optimizer.utils import list_intersection, get_positions_for_optimizer, get_remaining_positions
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.player import Player


if TYPE_CHECKING:
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
    def __init__(self, optimizer, params):
        super(NormalObjective, self).__init__(optimizer, params)
        self.used_combinations = []  # type: List[Any]

    def apply(self, solver, players_dict):
        variables = []
        coefficients = []
        for player, variable in players_dict.items():
            variables.append(variable)
            coefficients.append(player.fppg)
        solver.set_objective(variables, coefficients)

    def apply_for_iteration(self, solver, players_dict, result):
        if not result:
            return
        self.used_combinations.append([players_dict[player] for player in result])
        total_players = self.optimizer.total_players
        for variables in self.used_combinations:
            solver.add_constraint(variables, None, SolverSign.LTE, total_players - 1)


class RandomObjective(OptimizerRule):
    def apply_for_iteration(self, solver, players_dict, result):
        variables = []
        coefficients = []
        for player, variable in players_dict.items():
            variables.append(variable)
            coefficients.append(player.fppg * (1 + (-1 if bool(getrandbits(1)) else 1) *
                                               uniform(*self.optimizer.get_deviation())))
        solver.set_objective(variables, coefficients)


class TotalPlayersRule(OptimizerRule):
    def apply(self, solver, players_dict):
        variables = players_dict.values()
        coefficients = [1] * len(variables)
        solver.add_constraint(variables, coefficients, SolverSign.EQ, self.optimizer.total_players)


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
        self.remaining_iteration -= 1
        for player, variable in players_dict.items():
            if not player.min_exposure:
                continue
            if ceil(player.min_exposure * self.total_lineups) >= \
                    self.remaining_iteration - self.used_players.get(player, 0):
                solver.add_constraint([variable], None, SolverSign.EQ, 1)
        if not result:
            # First iteration, locked players must have exposure > 0
            for player in self.optimizer.locked_players:
                solver.add_constraint([players_dict[player]], None, SolverSign.EQ, 1)
            return
        for player in result.lineup:
            self.used_players[player] += 1
        removed_players = []
        for player, used in self.used_players.items():
            max_exposure = player.max_exposure if player.max_exposure is not None else self.params.get('max_exposure')
            if max_exposure is not None and max_exposure <= used / self.total_lineups:
                removed_players.append(player)
                solver.add_constraint([players_dict[player]], None, SolverSign.EQ, 0)
        for player in self.optimizer.locked_players:
            if player not in removed_players:
                solver.add_constraint([players_dict[player]], None, SolverSign.EQ, 1)


class PositionsRule(OptimizerRule):
    def apply(self, solver, players_dict):
        extra_positions = self.optimizer.players_with_same_position
        positions = get_positions_for_optimizer(self.optimizer.settings.positions)
        unique_positions = self.optimizer.available_positions
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
    def apply(self, solver, players_dict):
        from_same_team = len(self.optimizer.positions_from_same_team)
        players_combinations = []
        # Create all possible combinations with specified position for each team
        for team in self.optimizer.available_teams:
            team_players = [player for player in players_dict.keys() if player.team == team]
            players_by_positions = []
            for position in self.optimizer.positions_from_same_team:
                players_by_positions.append([player for player in team_players if position in player.positions])
            for players_combination in product(*players_by_positions):
                # Remove combinations with duplicated players
                if len(set(players_combination)) != from_same_team:
                    continue
                players_combinations.append(tuple([player for player in players_combination]))
        combinations_variable = {combination: solver.add_variable(
            'combinations_%d' % i
        ) for i, combination in enumerate(players_combinations)}
        solver.add_constraint(combinations_variable.values(), None, SolverSign.GTE, 1)
        for combination in players_combinations:
            variables = [players_dict[player] for player in combination]
            solver.add_constraint(variables, None, SolverSign.GTE,
                                  from_same_team * combinations_variable[combination])


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
        for players_combination in combinations(result.players, max_repeating_players + 1):
            self.exclude_combinations.append([players_dict[player] for player in players_combination])
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
    def apply(self, solver, players_dict):
        key_func = lambda t: t[0].full_name
        data = sorted(players_dict.items(), key=key_func)
        for player_id, group_iterator in groupby(data, key=key_func):
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
        positions = get_positions_for_optimizer(remaining_positions)
        for position, places in positions.items():
            players_with_position = [variable for player, variable in players_dict.items()
                                     if list_intersection(position, player.positions) and
                                     player not in unswappable_players]
            solver.add_constraint(players_with_position, None, SolverSign.GTE, places)
        # Exclude players with active games
        for player, variable in players_dict.items():
            if player not in unswappable_players and player.is_game_started:
                solver.add_constraint([players_dict[player]], None, SolverSign.EQ, 0)
        self.current_iteration += 1


class TeamStacksRule(OptimizerRule):
    def apply(self, solver, players_dict):
        stacks = self.optimizer.team_stacks
        players_by_teams = {
            team: [player for player in players_dict.keys() if player.team == team]
            for team in self.optimizer.available_teams
        }

        stacks_dict = {}
        for i, stack in enumerate(sorted(stacks, reverse=True), start=1):
            stacks_dict[stack] = i

        for stack, total in stacks_dict.items():
            combinations_variables = []

            for team, players in players_by_teams.items():
                solver_variable = solver.add_variable('teams_stack_%d_%s' % (stack, team))
                combinations_variables.append(solver_variable)
                variables = [players_dict[player] for player in players]
                solver.add_constraint(variables, None, SolverSign.GTE,
                                      stack * solver_variable)
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

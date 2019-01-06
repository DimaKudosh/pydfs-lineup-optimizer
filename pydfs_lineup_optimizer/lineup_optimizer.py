from __future__ import division
from collections import Counter, OrderedDict
from itertools import chain, permutations
from typing import List, FrozenSet, Tuple, Type, Generator, Set
from pydfs_lineup_optimizer.solvers import PuLPSolver, SolverException
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName
from pydfs_lineup_optimizer.sites import SitesRegistry
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition
from pydfs_lineup_optimizer.player import LineupPlayer
from pydfs_lineup_optimizer.utils import ratio
from pydfs_lineup_optimizer.rules import *


BASE_CONSTRAINTS = {TotalPlayersRule, LineupBudgetRule, PositionsRule, MaxFromOneTeamRule, LockedPlayersRule,
                    RemoveInjuredRule, UniquePlayerRule}


class LineupOptimizer(object):
    def __init__(self, settings, solver=PuLPSolver):
        # type: (Type[BaseSettings], Type[Solver]) -> None
        self._settings = settings
        self._csv_importer = None  # type: Optional[Type[CSVImporter]]
        self._constraints = BASE_CONSTRAINTS.copy()  # type: Set[Type[OptimizerRule]]
        self._players = []  # type: List[Player]
        self._lineup = []  # type: List[Player]
        self._available_positions = frozenset(chain.from_iterable(
            position.positions for position in self._settings.positions))
        self._available_teams = frozenset()  # type: FrozenSet[str]
        self._removed_players = []  # type: List[Player]
        self._search_threshold = 0.8
        self._min_deviation = 0.06
        self._max_deviation = 0.12
        self._players_from_one_team = {}  # type: Dict[str, int]
        self._players_with_same_position = {}  # type: Dict[str, int]
        self._positions_from_same_team = []  # type: List[str]
        self._min_salary_cap = None  # type: Optional[float]
        self._max_repeating_players = None  # type: Optional[int]
        self._solver_class = solver
        self._max_projected_ownership = None  # type: Optional[float]
        self._min_projected_ownership = None  # type: Optional[float]

    @property
    def budget(self):
        # type: () -> float
        return self._settings.budget

    @property
    def total_players(self):
        # type: () -> int
        return self._settings.get_total_players()

    @property
    def remaining_budget(self):
        # type: () -> float
        return self.budget - sum(player.salary for player in self.locked_players)

    @property
    def remaining_players(self):
        # type: () -> int
        return self.total_players - len(self.locked_players)

    @property
    def max_from_one_team(self):
        # type: () -> Optional[int]
        return self._settings.max_from_one_team

    @property
    def positions_from_same_team(self):
        # type: () -> List[str]
        return self._positions_from_same_team

    @property
    def players_from_one_team(self):
        # type: () -> Dict[str, int]
        return self._players_from_one_team

    @property
    def players_with_same_position(self):
        # type: () -> Dict[str, int]
        return self._players_with_same_position

    @property
    def available_teams(self):
        # type: () -> FrozenSet[str]
        return self._available_teams

    @property
    def available_positions(self):
        # type: () -> FrozenSet[LineupPosition]
        return self._available_positions

    @property
    def removed_players(self):
        # type: () -> List[Player]
        return self._removed_players

    @property
    def players(self):
        # type: () -> List[Player]
        return [player for player in self._players if player not in self.removed_players]

    @property
    def locked_players(self):
        # type: () -> List[Player]
        return self._lineup

    @property
    def min_salary_cap(self):
        # type: () -> Optional[float]
        return self._min_salary_cap

    @property
    def max_repeating_players(self):
        # type: () -> Optional[int]
        return self._max_repeating_players

    @property
    def max_projected_ownership(self):
        # type: () -> Optional[float]
        return self._max_projected_ownership

    @property
    def min_projected_ownership(self):
        # type: () -> Optional[float]
        return self._min_projected_ownership

    def reset_lineup(self):
        self._lineup = []
        self._players_with_same_position = {}
        self._players_from_one_team = {}
        self._positions_from_same_team = []

    def set_deviation(self, min_deviation, max_deviation):
        # type: (float, float) -> None
        """
        Set deviation ranges for randomness mode
        """
        self._min_deviation = min_deviation
        self._max_deviation = max_deviation

    def set_csv_importer(self, csv_importer):
        # type: (Type[CSVImporter]) -> None
        self._csv_importer = csv_importer

    def get_deviation(self):
        # type: () -> Tuple[float, float]
        return self._min_deviation, self._max_deviation

    def set_min_salary_cap(self, min_salary):
        # type: (float) -> None
        if min_salary > self.budget:
            raise LineupOptimizerException('Min salary greater than max budget')
        self.add_new_rule(MinSalaryCapRule)
        self._min_salary_cap = min_salary

    def load_players_from_csv(self, filename):
        # type: (str) -> None
        """
        Load player list from CSV file with passed filename.
        """
        csv_importer = self._csv_importer
        if not csv_importer:
            csv_importer = SitesRegistry.get_csv_importer(self._settings.site)
        self._players = csv_importer(filename).import_players()
        self._set_available_teams()

    def load_players(self, players):
        # type: (List[Player]) -> None
        """
        Manually loads player to optimizer
        """
        self._players = players
        self._set_available_teams()

    def extend_players(self, players):
        # type: (List[Player]) -> None
        """
        Add more players for current optimizer players
        """
        self._players.extend(players)
        self._set_available_teams()

    def get_positions_for_optimizer(self):
        # type: () -> Dict[Tuple[str, ...], int]
        """
        Convert positions list into dict for using in optimizer.
        """
        positions_list = self._settings.positions
        positions = {}
        positions_counter = Counter([tuple(sorted(p.positions)) for p in positions_list])
        for key in positions_counter.keys():
            min_value = positions_counter[key] + len(list(filter(
                lambda p: len(p.positions) < len(key) and list_intersection(key, p.positions), positions_list
            )))
            positions[key] = min_value
        for i in range(2, len(positions)):
            for positions_tuple in combinations(positions_counter.keys(), i):
                flatten_positions = tuple(sorted(chain.from_iterable(positions_tuple)))
                if len(flatten_positions) != len(set(flatten_positions)):
                    continue
                if flatten_positions in positions:
                    continue
                min_value = sum(positions[pos] for pos in positions_tuple)
                positions[flatten_positions] = min_value
        positions = OrderedDict(sorted(positions.items(), key=lambda item: len(item[0])))
        return positions

    def add_new_rule(self, rule):
        # type: (Type[OptimizerRule]) -> None
        self._constraints.add(rule)

    def remove_rule(self, rule, silent=True):
        # type: (Type[OptimizerRule], bool) -> None
        try:
            self._constraints.remove(rule)
        except KeyError:
            if not silent:
                raise LineupOptimizerException('Rule isn\'t added!')

    def remove_player(self, player):
        # type: (Player) -> None
        """
        Remove player from list for selecting players for lineup.
        """
        self._removed_players.append(player)

    def restore_player(self, player):
        # type: (Player) -> None
        """
        Restore removed player.
        """
        try:
            self._removed_players.remove(player)
        except ValueError:
            raise LineupOptimizerException('Player not removed!')

    def find_players(self, name):
        # type: (str) -> List[Player]
        """
        Return list of players with similar name.
        """
        possibilities = [(player, ratio(name, player.full_name)) for player in self._players]
        filtered_possibilities = filter(lambda pos: pos[1] >= self._search_threshold, possibilities)
        players = sorted(filtered_possibilities, key=lambda pos: -pos[1])
        return list(map(lambda p: p[0], players))

    def get_player_by_name(self, name):
        # type: (str) -> Optional[Player]
        """
        Return closest player with similar name or None.
        """
        players = self.find_players(name)
        return players[0] if players else None

    def add_player_to_lineup(self, player):
        # type: (Player) -> None
        """
        Forces adding specified player to lineup.
        Return true if player successfully added to lineup.
        """
        if player.max_exposure == 0:
            raise LineupOptimizerException('Can\'t add this player to line up! Player has max exposure set to 0.')
        if player in self._lineup:
            raise LineupOptimizerException('This player already in your line up!')
        if player.salary > self.remaining_budget:
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
            self._link_players_with_positions(self.locked_players + [player])
        except LineupOptimizerException:
            raise LineupOptimizerException('You\'re already select all %s\'s' % '/'.join(player.positions))
        self._lineup.append(player)

    def remove_player_from_lineup(self, player):
        # type: (Player) -> None
        """
        Removes specified player from lineup.
        """
        try:
            self._lineup.remove(player)
        except ValueError:
            raise LineupOptimizerException('Player not in line up!')

    def set_players_from_one_team(self, teams=None):
        # type: (Optional[Dict[str, int]]) -> None
        if teams is not None:
            teams = {team.upper(): num_of_players for team, num_of_players in teams.items()}
            for team, num_of_players in teams.items():
                self._check_team_constraint(team, num_of_players)
            self.add_new_rule(TeamMatesRule)
        else:
            self.remove_rule(TeamMatesRule)
        self._players_from_one_team = teams or {}

    def set_players_with_same_position(self, positions):
        # type: (Dict[str, int]) -> None
        positions = positions or {}
        positions = {position.upper(): num_of_players for position, num_of_players in positions.items()}
        for pos, val in positions.items():
            self._check_position_constraint(pos)
        self._players_with_same_position = positions

    def set_positions_for_same_team(self, positions):
        # type: (Optional[List[str]]) -> None
        if positions is not None:
            if self.max_from_one_team and len(positions) > self.max_from_one_team:
                raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                               self.max_from_one_team)
            positions = [position.upper() for position in positions]
            for position, num_of_players in Counter(positions).items():
                self._check_position_constraint(position)
            self.add_new_rule(FromSameTeamByPositionsRule)
        else:
            self.remove_rule(FromSameTeamByPositionsRule)
        self._positions_from_same_team = positions or []

    def set_max_repeating_players(self, max_repeating_players):
        # type: (int) -> None
        if max_repeating_players >= self.total_players:
            raise LineupOptimizerException('Maximum repeating players should be smaller than %d' % self.total_players)
        elif max_repeating_players < 1:
            raise LineupOptimizerException('Maximum repeating players should be 1 or greater')
        self._max_repeating_players = max_repeating_players
        self.add_new_rule(MaxRepeatingPlayersRule)

    def set_projected_ownership(self, min_projected_ownership=None, max_projected_ownership=None):
        # type: (Optional[float], Optional[float]) -> None
        if min_projected_ownership and max_projected_ownership and min_projected_ownership >= max_projected_ownership:
            raise LineupOptimizerException('Max projected ownership should be greater than min projected ownership')
        self._max_projected_ownership = max_projected_ownership / 100 if \
            max_projected_ownership and max_projected_ownership > 1 else max_projected_ownership
        self._min_projected_ownership = min_projected_ownership / 100 if \
            min_projected_ownership and min_projected_ownership > 1 else min_projected_ownership
        if max_projected_ownership or min_projected_ownership:
            self.add_new_rule(ProjectedOwnershipRule)
        else:
            self.remove_rule(ProjectedOwnershipRule)

    def optimize(self, n, max_exposure=None, randomness=False, with_injured=False):
        # type: (int, Optional[float], bool, bool) -> Generator[Lineup, None, None]
        params = locals()
        rules = self._constraints.copy()
        if randomness:
            rules.add(RandomObjective)
        else:
            rules.add(NormalObjective)
        if with_injured:
            rules.remove(RemoveInjuredRule)
        players = [player for player in self._players
                   if player not in self._removed_players and player.max_exposure != 0.0]
        base_solver = self._solver_class()
        base_solver.setup_solver()
        players_dict = OrderedDict(
            [(player, base_solver.add_variable('Player_%d' % i, 0, 1)) for i, player in enumerate(players)])
        variables_dict = {v: k for k, v in players_dict.items()}
        constraints = [constraint(self, params) for constraint in rules]
        for constraint in constraints:
            constraint.apply(base_solver, players_dict)
        previous_lineup = None
        for _ in range(n):
            solver = base_solver.copy()
            for constraint in constraints:
                constraint.apply_for_iteration(solver, players_dict, previous_lineup)
            try:
                solved_variables = solver.solve()
                lineup_players = []
                for solved_variable in solved_variables:
                    player = variables_dict.get(solved_variable)
                    if player:
                        lineup_players.append(player)
                lineup = self._build_lineup(lineup_players)
                previous_lineup = lineup
                yield lineup
                if len(self.locked_players) == self.total_players:
                    return
            except SolverException:
                raise LineupOptimizerException('Can\'t generate lineups')

    def _link_players_with_positions(self, players):
        # type: (List[Player]) -> Dict[Player, LineupPosition]
        """
        This method tries to set positions for given players, and raise error if can't.
        """
        positions = self._settings.positions[:]
        single_position_players = []  # type: List[Player]
        multi_positions_players = []  # type: List[Player]
        players_with_positions = {}  # type: Dict[Player, LineupPosition]
        for player in players:
            if len(player.positions) == 1:
                single_position_players.append(player)
            else:
                multi_positions_players.append(player)
        for player in single_position_players:
            for position in positions:
                if player.positions[0] in position.positions:
                    players_with_positions[player] = position
                    positions.remove(position)
                    break
            else:
                raise LineupOptimizerException('Unable to build lineup')
        for players_permutation in permutations(multi_positions_players):
            is_correct = True
            remaining_positions = positions[:]
            for player in players_permutation:
                for position in remaining_positions:
                    if list_intersection(player.positions, position.positions):
                        players_with_positions[player] = position
                        remaining_positions.remove(position)
                        break
                else:
                    is_correct = False
                    break
            if is_correct:
                break
        else:
            raise LineupOptimizerException('Unable to build lineup')
        return players_with_positions

    def _build_lineup(self, players):
        # type: (List[Player]) -> Lineup
        players_with_positions = self._link_players_with_positions(players)
        lineup = []
        for player, position in players_with_positions.items():
            lineup.append(LineupPlayer(player, position.name))
        positions_order = [pos.name for pos in self._settings.positions]
        lineup.sort(key=lambda p: positions_order.index(p.lineup_position))
        return Lineup(lineup, self._settings.lineup_printer)

    def _set_available_teams(self):
        """
        Evaluate all available teams.
        """
        self._available_teams = frozenset([p.team for p in self._players])

    def _check_team_constraint(self, team, num_of_players):
        # type: (str, int) -> None
        if team not in self.available_teams:
            raise LineupOptimizerIncorrectTeamName('%s is incorrect team name.' % team)
        if self.max_from_one_team and num_of_players > self.max_from_one_team:
            raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                           self.max_from_one_team)

    def _check_position_constraint(self, position):
        # type: (str) -> None
        if position not in self.available_positions:
            raise LineupOptimizerIncorrectPositionName('%s is incorrect position name.' % position)

from __future__ import division
from collections import Counter, OrderedDict, defaultdict
from itertools import chain, combinations, product
from copy import deepcopy
from random import getrandbits, uniform
from pulp import LpProblem, LpMaximize, LpVariable, LpInteger, lpSum, LpStatusOptimal
from .exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, LineupOptimizerIncorrectPositionName
from .settings import BaseSettings
from .player import Player
from .lineup import Lineup, LineupPlayer
from .utils import ratio, list_intersection


class PositionPlaces(object):
    """
    Helper class, used for converting positions from settings readable format to format for PuLP
    """
    def __init__(self, min_players, optional):
        self.min = min_players
        self._init_optional = optional
        self.optional = optional

    @property
    def max(self):
        return self.min + self.optional

    def add(self):
        if self.min:
            self.min -= 1
        else:
            self.optional -= 1 if self.optional else 0

    def remove(self):
        if self.optional < self._init_optional:
            self.optional += 1
        else:
            self.min += 1


class LineupOptimizer(object):
    def __init__(self, settings):
        """
        LineupOptimizer creates the best lineup for daily fantasy sports.
        :type settings: BaseSettings
        """
        self._players = []
        self._lineup = []
        self._available_positions = []
        self._available_teams = []
        self._positions = {}
        self._not_linked_positions = {}
        self._max_from_one_team = None
        self._settings = settings
        self._set_settings()
        self._removed_players = []
        self._search_threshold = 0.8
        self._min_deviation = 0.06
        self._max_deviation = 0.12
        self._players_from_one_team = {}
        self._players_with_same_position = {}
        self._positions_from_same_team = []
        self._min_salary_cap = None

    @property
    def lineup(self):
        """
        :rtype: list[Player]
        """
        return self._lineup

    @property
    def budget(self):
        """
        :rtype: int
        """
        return self._budget

    @property
    def players(self):
        """
        :rtype: list[Player]
        """
        return [player for player in self._players
                if player not in self._removed_players and player not in self._lineup]

    @property
    def removed_players(self):
        """
        :rtype: list[Player]
        """
        return self._removed_players

    def _set_settings(self):
        """
        Set settings with daily fantasy sport site and kind of sport to optimizer.
        """
        self._budget = self._settings.budget
        self._total_players = self._settings.get_total_players()
        self._max_from_one_team = self._settings.max_from_one_team
        self._get_positions_for_optimizer(self._settings.positions)
        self._available_positions = self._positions.keys()

    def _get_positions_for_optimizer(self, positions_list):
        """
        Convert positions list into dict for using in optimizer.
        :type positions_list: List[LineupPosition]
        """
        positions = {}
        not_linked_positions = {}
        positions_counter = Counter([tuple(sorted(p.positions)) for p in positions_list])
        for key in positions_counter.keys():
            additional_pos = len(list(filter(
                lambda p: len(p.positions) > len(key) and list_intersection(key, p.positions), positions_list
            )))
            min_value = positions_counter[key] + len(list(filter(
                lambda p: len(p.positions) < len(key) and list_intersection(key, p.positions), positions_list
            )))
            positions[key] = PositionPlaces(min_value, additional_pos)
        for first_position, second_position in combinations(positions.items(), 2):
            if list_intersection(first_position[0], second_position[0]):
                continue
            new_key = tuple(sorted(chain(first_position[0], second_position[0])))
            if new_key in positions:
                continue
            not_linked_positions[new_key] = PositionPlaces(
                first_position[1].min + second_position[1].min,
                first_position[1].optional + second_position[1].optional
            )
        positions = OrderedDict(sorted(positions.items(), key=lambda item: len(item[0])))
        self._not_linked_positions = not_linked_positions
        self._positions = positions
        self._init_positions = positions

    def set_deviation(self, min_deviation, max_deviation):
        """
        Set deviation ranges for randomness mode
        :type min_deviation: float
        :type max_deviation: float
        """
        self._min_deviation = min_deviation
        self._max_deviation = max_deviation

    def set_min_salary_cap(self, min_salary):
        if min_salary > self._budget:
            raise LineupOptimizerException('Min salary greater than max budget')
        self._min_salary_cap = min_salary

    def reset_lineup(self):
        """
        Reset current lineup.
        """
        self._set_settings()
        self._lineup = []
        self._players_with_same_position = {}
        self._players_from_one_team = {}
        self._positions_from_same_team = []

    def load_players_from_CSV(self, filename):
        """
        Load player list from CSV file with passed filename.
        Calls load_players_from_CSV method from _settings object.
        :type filename: str
        """
        self._players = self._settings.load_players_from_CSV(filename)
        self._set_available_teams()

    def load_players(self, players):
        """
        Manually loads player to optimizer
        :type players: List[Player]
        """
        self._players = players
        self._set_available_teams()

    def _set_available_teams(self):
        """
        Evaluate all available teams.
        """
        self._available_teams = set([p.team for p in self._players])

    def remove_player(self, player):
        """
        Remove player from list for selecting players for lineup.
        :type player: Player
        """
        self._removed_players.append(player)

    def restore_player(self, player):
        """
        Restore removed player.
        :type player: Player
        """
        try:
            self._removed_players.remove(player)
        except ValueError:
            raise LineupOptimizerException('Player not removed!')

    def _add_to_lineup(self, player):
        """
        Adding player to lineup without checks
        :type player: Player
        """
        self._lineup.append(player)
        self._total_players -= 1
        self._budget -= player.salary

    def find_players(self, name):
        """
        Return list of players with similar name.
        :type name: str
        :return: List[Player]
        """
        players = self.players
        possibilities = [(player, ratio(name, player.full_name)) for player in players]
        possibilities = filter(lambda pos: pos[1] >= self._search_threshold, possibilities)
        players = sorted(possibilities, key=lambda pos: -pos[1])
        return list(map(lambda p: p[0], players))

    def get_player_by_name(self, name):
        """
        Return closest player with similar name or None.
        :type name: str
        :return: Player
        """
        players = self.find_players(name)
        return players[0] if players else None

    def _recalculate_positions(self, players):
        """
        Realculates available positions for optimizer with locked specified players.
        Return dict with positions for optimizer and number of placed players.
        :type players: List[Player]
        :return: Dict, int
        """
        positions = deepcopy(self._init_positions)
        players.sort(key=lambda p: len(p.positions))
        total_added = 0
        for player in players:
            is_added = False
            changed_positions = []
            for position, places in positions.items():
                if not list_intersection(player.positions, position):
                    continue
                if not places.max and list(player.positions) == list(position):
                    is_added = False
                    break
                is_added = True
                changed_positions.append(position)
            if is_added:
                total_added += 1
                [positions[position].add() for position in changed_positions]
        return positions, total_added

    def add_player_to_lineup(self, player):
        """
        Forces adding specified player to lineup.
        Return true if player successfully added to lineup.
        :type player: Player
        """
        if player.max_exposure == 0:
            raise LineupOptimizerException('Can\'t add this player to line up! Player has max exposure set to 0.')
        if player in self._lineup:
            raise LineupOptimizerException('This player already in your line up!')
        if not isinstance(player, Player):
            raise LineupOptimizerException('This function accept only Player objects!')
        if self._budget - player.salary < 0:
            raise LineupOptimizerException('Can\'t add this player to line up! Your team is over budget!')
        if self._total_players - 1 < 0:
            raise LineupOptimizerException('Can\'t add this player to line up! You already select all %s players!' %
                                           len(self._lineup))
        if self._max_from_one_team:
            from_same_team = len(list(filter(lambda p: p.team == player.team, self.lineup)))
            if from_same_team + 1 > self._max_from_one_team:
                raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                               self._max_from_one_team)
        players = self.lineup[:]
        players.append(player)
        positions, total_added = self._recalculate_positions(players)
        if total_added == len(players):
            self._add_to_lineup(player)
            self._positions = positions
            for position, places in self._not_linked_positions.items():
                if list_intersection(position, player.positions):
                    self._not_linked_positions[position].add()
        else:
            raise LineupOptimizerException('You\'re already select all %s\'s' % '/'.join(player.positions))

    def remove_player_from_lineup(self, player):
        """
        Removes specified player from lineup.
        :type player: Player
        """
        if not isinstance(player, Player):
            raise LineupOptimizerException('This function accept only Player objects!')
        try:
            self._lineup.remove(player)
            self._budget += player.salary
            self._total_players += 1
            for position, places in self._positions.items():
                if list_intersection(position, player.positions):
                    self._positions[position].remove()
            for position, places in self._not_linked_positions.items():
                if list_intersection(position, player.positions):
                    self._not_linked_positions[position].remove()
        except ValueError:
            raise LineupOptimizerException('Player not in line up!')

    def _build_lineup(self, players):
        """
        Creates lineup after optimizer run, set position name like in dfs site for players
        :type players: list[Player]
        :return: Lineup
        """
        players_with_position = []
        positions = self._settings.positions[:]
        positions_order = [pos.name for pos in positions]
        single_position_players = []
        multi_positions_players = []
        # Split single and multiple positions players
        for player in players:
            if len(player.positions) == 1:
                single_position_players.append(player)
            else:
                multi_positions_players.append(player)
        # Firstly set positions for single position players
        for player in single_position_players:
            for position in positions:
                if list_intersection(player.positions, position.positions):
                    players_with_position.append(LineupPlayer(player, position.name))
                    positions.remove(position)
                    break
            else:
                raise LineupOptimizerException('Unable to build lineup from optimizer result')
        # Set positions for multi-positional players
        # Create list of eligible players for each position
        position_eligible_players = []
        for position in positions:
            position_eligible_players.append((position, [player for player in multi_positions_players
                                                         if list_intersection(player.positions, position.positions)]))

        players_appearance_counter = Counter(chain(*[p[1] for p in position_eligible_players]))
        # Select position with fewest eligible players and set players with fewest allowed positions to this position
        for _ in range(len(position_eligible_players)):
            position_eligible_players.sort(key=lambda p: len(p[1]))
            selected_position, eligible_players = position_eligible_players.pop(0)
            eligible_players.sort(key=lambda p: players_appearance_counter[p])
            try:
                player = eligible_players[0]
            except IndexError:
                raise LineupOptimizerException('Unable to build lineup from optimizer result')
            players_with_position.append(LineupPlayer(player, selected_position.name))
            # Remove selected player from eligible players for other positions
            del players_appearance_counter[player]
            for _, other_player_positions in position_eligible_players:
                try:
                    other_player_positions.remove(player)
                except ValueError:
                    pass
            # Decrease players counter for other players that can be set to this position
            for p in eligible_players[1:]:
                players_appearance_counter[p] -= 1
        players_with_position.sort(key=lambda p: positions_order.index(p.lineup_position))
        return Lineup(players_with_position)

    def _check_team_constraint(self, team, num_of_players):
        if team not in self._available_teams:
            raise LineupOptimizerIncorrectTeamName('%s is incorrect team name.' % team)
        if self._max_from_one_team and num_of_players > self._max_from_one_team:
            raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                           self._max_from_one_team)

    def _check_position_constraint(self, position, num_of_positions):
        if (position,) not in self._available_positions:
            raise LineupOptimizerIncorrectPositionName('%s is incorrect position name.' % position)
        available_places = self._positions[(position,)].max
        if num_of_positions > available_places:
            raise LineupOptimizerException('Max available places for position %s is %s. Got %s' %
                                           (position, available_places, num_of_positions))

    def set_players_from_one_team(self, teams=None):
        """
        :type teams: dict[str, int]|None
        """
        teams = teams or {}
        teams = {team.upper(): num_of_players for team, num_of_players in teams.items()}
        for team, num_of_players in teams.items():
            self._check_team_constraint(team, num_of_players)
        self._players_from_one_team = teams

    def set_players_with_same_position(self, positions):
        """
        :type positions:
        :return: positions: dict[str, int]|None
        """
        positions = positions or {}
        positions = {position.upper(): num_of_players for position, num_of_players in positions.items()}
        for pos, val in positions.items():
            self._check_position_constraint(pos, val)
        self._players_with_same_position = positions

    def set_positions_for_same_team(self, positions):
        """
        :type positions: list[str]
        """
        positions = positions or []
        if self._max_from_one_team and len(positions) > self._max_from_one_team:
            raise LineupOptimizerException('You can\'t set more than %s players from one team.' %
                                           self._max_from_one_team)
        positions = [position.upper() for position in positions]
        for position, num_of_players in Counter(positions).items():
            self._check_position_constraint(position, num_of_players)
        self._positions_from_same_team = positions

    def optimize(self, n, max_exposure=None, randomness=None, with_injured=False):
        """
        Select optimal lineup from players list.
        This method uses Mixed Integer Linear Programming method for evaluating best starting lineup.
        It"s return generator. If you don't specify n it will return generator with all possible lineups started
        from highest fppg to lowest fppg.
        :type n: int
        :type max_exposure: float
        :type randomness: bool
        :type with_injured: bool
        :rtype: list[Lineup]
        """
        teams, positions = self._players_from_one_team, self._players_with_same_position
        # Check for empty places
        if len(self._lineup) == self._settings.get_total_players():
            lineup = self._build_lineup(self._lineup)
            yield lineup
            return
        locked_players = self._lineup[:]
        players = [player for player in self._players
                   if player not in self._removed_players and player not in self._lineup
                   and isinstance(player, Player) and player.max_exposure != 0.0]
        current_max_points = 10000000
        lineup_points = sum(player.fppg for player in self._lineup)
        used_players = defaultdict(int)
        min_salary_cap = self._min_salary_cap - sum((p.salary for p in self._lineup)) if self._min_salary_cap else None
        for _ in range(n):
            # filter players with exceeded max exposure
            for player, used in used_players.items():
                exposure = player.max_exposure if player.max_exposure is not None else max_exposure
                if exposure is not None and exposure <= used / n:
                    if player in players:
                        players.remove(player)
                    if player in self.lineup:
                        self.remove_player_from_lineup(player)
                        current_max_points += player.fppg
                        lineup_points -= player.fppg
            prob = LpProblem('Daily Fantasy Sports', LpMaximize)
            x = LpVariable.dicts(
                'players', players,
                lowBound=0,
                upBound=1,
                cat=LpInteger
            )
            #  Add random for projections
            if randomness:
                for i, player in enumerate(players):
                    player.deviated_fppg = player.fppg * (1 + (-1 if bool(getrandbits(1)) else 1) *
                                                          uniform(self._min_deviation, self._max_deviation))
                prob += lpSum([player.deviated_fppg * x[player] for player in players])
            else:
                prob += lpSum([player.fppg * x[player] for player in players])
                prob += lpSum([player.fppg * x[player] for player in players]) <= current_max_points
            prob += lpSum([player.salary * x[player] for player in players]) <= self._budget
            if min_salary_cap:
                prob += lpSum([player.salary * x[player] for player in players]) >= min_salary_cap
            prob += lpSum([x[player] for player in players]) == self._total_players
            if not with_injured:
                prob += lpSum([x[player] for player in players if not player.is_injured]) == self._total_players
            for position, places in self._positions.items():
                extra = 0
                if len(position) == 1:
                    extra = positions.get(position[0], 0)
                prob += lpSum([x[player] for player in players if
                               any([player_position in position for player_position in player.positions])
                               ]) >= places.min + extra
            for position, places in self._not_linked_positions.items():
                prob += lpSum([x[player] for player in players if
                               any([player_position in position for player_position in player.positions])
                               ]) >= places.min
            if teams is not None:
                for key, value in teams.items():
                    prob += lpSum([x[player] for player in players if player.team == key]) == value
            if self._max_from_one_team:
                for team in self._available_teams:
                    prob += lpSum([x[player] for player in players if player.team == team]) <= self._max_from_one_team
            if self._positions_from_same_team:
                from_same_team = len(self._positions_from_same_team)
                players_combinations = []
                # Create all possible combinations with specified position for each team
                for team in self._available_teams:
                    team_players = [player for player in players if player.team == team]
                    players_by_positions = []
                    for position in self._positions_from_same_team:
                        players_by_positions.append([player for player in team_players if position in player.positions])
                    for players_combination in product(*players_by_positions):
                        # Remove combinations with duplicated players
                        if len(set(players_combination)) != from_same_team:
                            continue
                        players_combinations.append(tuple([player for player in players_combination]))
                combinations_variable = LpVariable.dicts(
                    'combinations', players_combinations,
                    lowBound=0,
                    upBound=1,
                    cat=LpInteger
                )
                prob += lpSum([combinations_variable[combination] for combination in players_combinations]) >= 1
                for combination in players_combinations:
                    prob += sum(x[player] for player in combination) >= \
                            from_same_team * combinations_variable[combination]

            prob.solve()
            if prob.status == LpStatusOptimal:
                lineup_players = self._lineup[:]
                for player in players:
                    if x[player].value() == 1.0:
                        lineup_players.append(player)
                for player in lineup_players:
                    used_players[player] += 1
                lineup = self._build_lineup(lineup_players)
                current_max_points = lineup.fantasy_points_projection - lineup_points - 0.001
                yield lineup
            else:
                raise LineupOptimizerException('Can\'t generate lineups')
        self._lineup = locked_players
        return

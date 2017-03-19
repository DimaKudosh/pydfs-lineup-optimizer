from __future__ import division
from collections import Counter, OrderedDict, defaultdict
from itertools import chain, combinations
from copy import deepcopy
from pulp import *
from .exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, LineupOptimizerIncorrectPositionName
from .settings import BaseSettings
from .player import Player
from .lineup import Lineup
from .utils import ratio, list_intersection


class PositionPlaces:
    def __init__(self, min, optional):
        self.min = min
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
        LineupOptimizer select the best lineup for daily fantasy sports.
        :type settings: BaseSettings
        """
        self._players = []
        self._lineup = []
        self._available_positions = []
        self._available_teams = []
        self._positions = {}
        self._not_linked_positions = {}
        self._settings = settings
        self._set_settings()
        self._removed_players = []
        self._search_threshold = 0.8

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
        :type settings: BaseSettings
        """
        self._budget = self._settings.budget
        self._total_players = self._settings.total_players
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

    def reset_lineup(self):
        """
        Reset current lineup.
        """
        self._set_settings()
        self._lineup = []

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
            pass

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
        :param name: str
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
        :param name: str
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
        Force adding specified player to lineup.
        Return true if player successfully added to lineup.
        :type player: Player
        """
        if player in self._lineup:
            raise LineupOptimizerException("This player already in your line up!")
        if not isinstance(player, Player):
            raise LineupOptimizerException("This function accept only Player objects!")
        if self._budget - player.salary < 0:
            raise LineupOptimizerException("Can't add this player to line up! Your team is over budget!")
        if self._total_players - 1 < 0:
            raise LineupOptimizerException("Can't add this player to line up! You already select all {} players!".
                                           format(len(self._lineup)))
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
            raise LineupOptimizerException("You're already select all {}'s".format("/".join(player.positions)))

    def remove_player_from_lineup(self, player):
        """
        Remove specified player from lineup.
        :type player: Player
        """
        if not isinstance(player, Player):
            raise LineupOptimizerException("This function accept only Player objects!")
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
            raise LineupOptimizerException("Player not in line up!")

    def _validate_optimizer_params(self, teams=None, positions=None):
        """
        Validate passed to optimizer parameters.
        :type teams: dict[str, int]
        :type positions: dict[str, int]
        :return: processed teams and positions
        """
        # check teams parameter
        if teams:
            if not isinstance(teams, dict) or not all([isinstance(team, str) for team in teams.keys()]) or \
                    not all([isinstance(num_of_players, int) for num_of_players in teams.values()]):
                raise LineupOptimizerException("Teams parameter must be dict where key is team name and value is number"
                                               " of players from specified team.")
            teams = {team.upper(): num_of_players for team, num_of_players in teams.items()}
            _teams = teams.keys()
            for team in _teams:
                if team not in self._available_teams:
                    raise LineupOptimizerIncorrectTeamName("{} is incorrect team name.".format(team))
        # check positions parameter
        if positions:
            if not isinstance(positions, dict) or \
                    not all([isinstance(position, str) for position in positions.keys()]) or \
                    not all([isinstance(num_of_players, int) for num_of_players in positions.values()]):
                raise LineupOptimizerException("Positions parameter must be dict where key is position name and value "
                                               "is number of players from specified position.")
            positions = {position.upper(): num_of_players for position, num_of_players in positions.items()}
            for pos, val in positions.items():
                available_places = self._positions[(pos,)].optional
                if val > self._positions[(pos,)].optional:
                    raise LineupOptimizerException("Max available places for position {} is {}. Got {} ".
                                                   format(pos, available_places, val))
                if (pos,) not in self._available_positions:
                    raise LineupOptimizerIncorrectPositionName("{} is incorrect position name.".format(pos))
        else:
            positions = {}
        return teams, positions

    def optimize(self, n,  teams=None, positions=None, max_exposure=None, with_injured=False):
        """
        Select optimal lineup from players list.
        This method uses Mixed Integer Linear Programming method for evaluating best starting lineup.
        It"s return generator. If you don"t specify n it will return generator with all possible lineups started
        from highest fppg to lowest fppg.
        :type n: int
        :type teams: dict[str, int]
        :type positions: dict[str, int]
        :type max_exposure: float
        :type with_injured: bool
        :rtype: List[Lineup]
        """
        teams, positions = self._validate_optimizer_params(teams, positions)
        if len(self._lineup) == self._settings.total_players:
            lineup = Lineup(self._lineup)
            yield lineup
            return
        locked_players = self._lineup[:]
        players = [player for player in self._players
                   if player not in self._removed_players and player not in self._lineup
                   and isinstance(player, Player) and player.max_exposure != 0.0]
        for player in self._lineup:
            if player.max_exposure == 0:
                self.remove_player_from_lineup(player)
        current_max_points = 10000000
        lineup_points = sum(player.fppg for player in self._lineup)
        used_players = defaultdict(int)
        counter = 0
        while n > counter:
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
            prob = LpProblem("Daily Fantasy Sports", LpMaximize)
            x = LpVariable.dicts(
                "table", players,
                lowBound=0,
                upBound=1,
                cat=LpInteger
            )
            prob += sum([player.fppg * x[player] for player in players])
            prob += sum([player.fppg * x[player] for player in players]) <= current_max_points
            prob += sum([player.salary * x[player] for player in players]) <= self._budget
            prob += sum([x[player] for player in players]) == self._total_players
            if not with_injured:
                prob += sum([x[player] for player in players if not player.is_injured]) == self._total_players
            for position, places in self._positions.items():
                extra = 0
                if len(position) == 1:
                    extra = positions.get(position[0], 0)
                prob += sum([x[player] for player in players if
                             any([player_position in position for player_position in player.positions])
                             ]) >= places.min + extra
            for position, places in self._not_linked_positions.items():
                prob += sum([x[player] for player in players if
                             any([player_position in position for player_position in player.positions])
                             ]) >= places.min
            if teams is not None:
                for key, value in teams.items():
                    prob += sum([x[player] for player in players if player.team == key]) == value
            prob.solve()
            if prob.status == 1:
                lineup_players = self._lineup[:]
                for player in players:
                    if x[player].value() == 1.0:
                        lineup_players.append(player)
                for player in lineup_players:
                    used_players[player] += 1
                lineup = Lineup(lineup_players)
                current_max_points = lineup.fantasy_points_projection - lineup_points - 0.001
                yield lineup
                counter += 1
            else:
                raise LineupOptimizerException("Can't generate lineups")
        self._lineup = locked_players
        return

from __future__ import division
from typing import Dict, Tuple, List, Iterable, Set, Any, DefaultDict, Optional, TYPE_CHECKING
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations, chain, permutations
from pydfs_lineup_optimizer.settings import LineupPosition
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.player import Player, LineupPlayer


def list_intersection(first_list, second_list):
    # type: (Iterable[Any], Iterable[Any]) -> bool
    for el in first_list:
        if el in second_list:
            return True
    return False


def ratio(search_string, possible_match):
    # type: (str, str) -> float
    search_string = search_string.lower()
    possible_match = possible_match.lower()
    if len(search_string) >= len(possible_match):
        parts = [possible_match]
    else:
        shorter_length = len(search_string)
        num_of_parts = len(possible_match) - shorter_length
        parts = [possible_match[i:i + shorter_length] for i in range(num_of_parts + 1)]
    return max([SequenceMatcher(None, search_string, part).ratio() for part in parts])


def get_positions_for_optimizer(positions_list, multi_positions_combinations=None):
    # type: (List[LineupPosition], Set[Tuple[str, ...]]) -> Dict[Tuple[str, ...], int]
    """
    Convert positions list into dict for using in optimizer.
    """
    positions = {}
    positions_counter = Counter([tuple(sorted(p.positions)) for p in positions_list])
    for key in positions_counter.keys():
        min_value = positions_counter[key] + len(list(filter(
            lambda p: len(p.positions) < len(key) and list_intersection(key, p.positions), positions_list
        )))
        positions[key] = min_value
    if not multi_positions_combinations:
        return positions
    #  Create list of required combinations for consistency of multi-positions
    for i in range(2, len(multi_positions_combinations)):
        total_combinations = len(multi_positions_combinations)
        for positions_tuple in combinations(multi_positions_combinations, i):
            flatten_positions = tuple(sorted(set(chain.from_iterable(positions_tuple))))
            multi_positions_combinations.add(flatten_positions)
        if total_combinations == len(multi_positions_combinations):
            break
    multi_positions_combinations.update(positions.keys())
    for i in range(2, len(positions)):
        for positions_tuple in combinations(positions_counter.keys(), i):
            flatten_positions = tuple(sorted(set(chain.from_iterable(positions_tuple))))
            if flatten_positions in positions or flatten_positions not in multi_positions_combinations:
                continue
            min_value = sum(positions[pos] for pos in positions_tuple)
            positions[flatten_positions] = min_value
    return positions


def link_players_with_positions(players, positions):
    # type: (List['Player'], List[LineupPosition]) -> Dict['Player', LineupPosition]
    """
    This method tries to set positions for given players, and raise error if can't.
    """
    positions = positions[:]
    single_position_players = []  # type: List['Player']
    multi_positions_players = []  # type: List['Player']
    players_with_positions = {}  # type: Dict['Player', LineupPosition]
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


def get_remaining_positions(positions, unswappable_players):
    # type: (List[LineupPosition], List['LineupPlayer']) -> List[LineupPosition]
    """
    Remove unswappable players positions from positions list
    """
    positions = positions[:]
    for player in unswappable_players:
        for position in positions:
            if position.name == player.lineup_position:
                positions.remove(position)
                break
    return positions


def get_players_grouped_by_teams(players):
    # type: (Iterable['Player']) -> DefaultDict[str, List['Player']]
    players_by_teams = defaultdict(list)  # type: DefaultDict[str, List['Player']]
    for player in players:
        players_by_teams[player.team].append(player)
    return players_by_teams


def process_percents(percent):
    # type: (Optional[float]) -> Optional[float]
    return percent / 100 if percent and percent > 1 else percent

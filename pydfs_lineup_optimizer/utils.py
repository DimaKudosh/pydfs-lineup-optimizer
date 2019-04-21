from typing import Dict, Tuple, List, Iterable, Any
from collections import Counter
from difflib import SequenceMatcher
from itertools import combinations, chain, permutations
from pydfs_lineup_optimizer.player import Player, LineupPlayer
from pydfs_lineup_optimizer.settings import LineupPosition
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException


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


def get_positions_for_optimizer(positions_list):
    # type: (List[LineupPosition]) -> Dict[Tuple[str, ...], int]
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
    for i in range(2, len(positions)):
        for positions_tuple in combinations(positions_counter.keys(), i):
            flatten_positions = tuple(sorted(chain.from_iterable(positions_tuple)))
            if len(flatten_positions) != len(set(flatten_positions)):
                continue
            if flatten_positions in positions:
                continue
            min_value = sum(positions[pos] for pos in positions_tuple)
            positions[flatten_positions] = min_value
    return positions


def link_players_with_positions(players, positions):
    # type: (List[Player], List[LineupPosition]) -> Dict[Player, LineupPosition]
    """
    This method tries to set positions for given players, and raise error if can't.
    """
    positions = positions[:]
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


def get_remaining_positions(positions, unswappable_players):
    # type: (List[LineupPosition], List[LineupPlayer]) -> List[LineupPosition]
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

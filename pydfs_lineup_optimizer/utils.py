import warnings
from typing import Dict, Tuple, List, Iterable, Set, Any, DefaultDict, Optional, TYPE_CHECKING
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import combinations, chain, permutations
from pydfs_lineup_optimizer.settings import LineupPosition
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.player import Player, LineupPlayer


def list_intersection(first_list: Iterable[Any], second_list: Iterable[Any]) -> bool:
    for el in first_list:
        if el in second_list:
            return True
    return False


def ratio(search_string: str, possible_match: str) -> float:
    search_string = search_string.lower()
    possible_match = possible_match.lower()
    if len(search_string) >= len(possible_match):
        parts = [possible_match]
    else:
        shorter_length = len(search_string)
        num_of_parts = len(possible_match) - shorter_length
        parts = [possible_match[i:i + shorter_length] for i in range(num_of_parts + 1)]
    return max([SequenceMatcher(None, search_string, part).ratio() for part in parts])


def get_positions_for_optimizer(
        positions_list: List[LineupPosition],
        multi_positions_combinations: Optional[Set[Tuple[str, ...]]] = None
) -> Dict[Tuple[str, ...], int]:
    """
    Convert positions list into dict for using in optimizer.
    """
    positions = {}
    positions_counter = Counter(p.positions for p in positions_list)
    for key, total in positions_counter.items():
        min_value = total + len(list(filter(
            lambda p: len(p.positions) < len(key) and list_intersection(key, p.positions), positions_list
        )))
        positions[key] = min_value
    if not multi_positions_combinations:
        return positions
    # Create min partition for each position
    min_positions = {}  # type: Dict[str, Tuple[str, ...]]
    for positions_tuple in positions_counter.keys():
        for position in positions_tuple:
            if position not in min_positions or len(min_positions[position]) > len(positions_tuple):
                min_positions[position] = positions_tuple
    #  Create list of required combinations for consistency of multi-positions
    possible_combinations = set()
    for multi_positions in multi_positions_combinations:
        possible_combinations.add(tuple(chain.from_iterable(min_positions.get(pos, (pos, )) for pos in multi_positions)))
    for i in range(2, len(possible_combinations) + 1):
        total_combinations = len(possible_combinations)
        for combo in combinations(possible_combinations, i):
            flatten_positions = tuple(sorted(set(chain.from_iterable(combo))))
            possible_combinations.add(flatten_positions)
        if total_combinations == len(possible_combinations):
            break
    # Calculate min required players for each position
    possible_combinations.update(positions.keys())
    for i in range(2, len(positions)):
        for combo in combinations(positions_counter.keys(), i):
            flatten_positions = tuple(sorted(set(chain.from_iterable(combo))))
            if flatten_positions in positions or flatten_positions not in possible_combinations:
                continue
            min_value = sum(positions[pos] for pos in combo)
            positions[flatten_positions] = min_value
    return positions


def link_players_with_positions(
        players: Iterable['Player'],
        positions: List[LineupPosition]
) -> Dict['Player', LineupPosition]:
    """
    This method tries to set positions for given players, and raise error if can't.
    """
    positions = positions.copy()
    players_with_positions = {}  # type: Dict['Player', LineupPosition]
    players = sorted(players, key=get_player_priority)
    for position in positions:
        players_for_position = [p for p in players if list_intersection(position.positions, p.positions)]
        if len(players_for_position) == 1:
            players_with_positions[players_for_position[0]] = position
            positions.remove(position)
            players.remove(players_for_position[0])
    for players_permutation in permutations(players):
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


def get_remaining_positions(
        positions: List[LineupPosition],
        unswappable_players: Optional[List['LineupPlayer']] = None,
        locked_positions: Optional[List['LineupPosition']] = None,
) -> List[LineupPosition]:
    """
    Remove locked and unswappable players positions from positions list
    """
    positions = positions[:]
    for player in unswappable_players or []:
        for position in positions:
            if position.name == player.lineup_position:
                positions.remove(position)
                break
    for locked_position in locked_positions or []:
        for position in positions:
            if position.name == locked_position.name:
                positions.remove(position)
                break
    return positions


def get_players_grouped_by_teams(
        players: Iterable['Player'],
        for_teams: Optional[List[str]] = None,
        for_positions: Optional[List[str]] = None,
) -> DefaultDict[str, List['Player']]:
    players_by_teams = defaultdict(list)  # type: DefaultDict[str, List['Player']]
    for player in players:
        if for_teams is not None and player.team not in for_teams:
            continue
        if for_positions is not None and not list_intersection(player.positions, for_positions):
            continue
        players_by_teams[player.team].append(player)
    return players_by_teams


def get_player_priority(player: 'Player') -> float:
    return float(player.game_info.starts_at.timestamp()) if player.game_info and player.game_info.starts_at else 0.0


def show_deprecation_warning(text: str):
    warnings.simplefilter('always', DeprecationWarning)
    warnings.warn(text, DeprecationWarning)

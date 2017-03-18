from difflib import SequenceMatcher


def list_intersection(first_list, second_list):
    return set(first_list).intersection(set(second_list))


def ratio(search_string, possible_match):
    search_string = search_string.lower()
    possible_match = possible_match.lower()
    if len(search_string) >= len(possible_match):
        parts = [possible_match]
    else:
        shorter_length = len(search_string)
        num_of_parts = len(possible_match) - shorter_length
        parts = [possible_match[i:i + shorter_length] for i in range(num_of_parts + 1)]
    return max([SequenceMatcher(None, search_string, part).ratio() for part in parts])

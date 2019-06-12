import json
from pydfs_lineup_optimizer.player import Player


class PlayersLoader:
    """
    Helper class for avoiding extra reading of players json
    """
    def __init__(self):
        self.cache = None

    def __call__(self):
        if self.cache:
            return self.cache[:]
        with open('tests/players.json', 'r') as file:
            players_dict = json.loads(file.read())['players']
        players = [Player(
            p['id'],
            p['first_name'],
            p['last_name'],
            p['positions'],
            p['team'],
            p['salary'],
            p['fppg']
        ) for i, p in enumerate(players_dict)]
        self.cache = players
        return players[:]


load_players = PlayersLoader()


def create_players(positions_list, **kwargs):
    params = {
        'salary': 10,
        'fppg': 10
    }
    params.update(kwargs)
    players = []
    for i, positions in enumerate(positions_list):
        player_params = {'team': str(i)}
        player_params.update(params)
        players.append(
            Player(player_id=str(i), first_name=str(i), last_name=str(i), positions=positions.split('/'),
                   **player_params)
        )
    return players


def count_players_in_lineups(players, lineups):
    lineups_with_players = {player: 0 for player in players}
    for lineup in lineups:
        for player in players:
            if player in lineup:
                lineups_with_players[player] += 1
    return lineups_with_players

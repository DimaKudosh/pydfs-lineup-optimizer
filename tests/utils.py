import json
from pydfs_lineup_optimizer.player import Player


def load_players():
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
        ) for p in players_dict]
    return players


def create_players(positions_list, **kwargs):
    params = {
        'salary': 10,
        'fppg': 10
    }
    params.update(kwargs)
    players = []
    for i, positions in enumerate(positions_list):
        players.append(
            Player(player_id=i, first_name=str(i), last_name=str(i), positions=positions.split('/'), team=str(i),
                   **params)
        )
    return players

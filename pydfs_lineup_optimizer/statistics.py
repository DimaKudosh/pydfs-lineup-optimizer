from typing import TYPE_CHECKING, DefaultDict, Dict
from collections import Counter, defaultdict, OrderedDict
from itertools import chain
from pydfs_lineup_optimizer.player import LineupPlayer


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer


class Statistic:
    def __init__(self, optimizer: 'LineupOptimizer', with_excluded: bool = True):
        self.optimizer = optimizer
        if self.optimizer.last_context is not None:
            self.lineups = self.optimizer.last_context.get_lineups(with_excluded)
        else:
            self.lineups = []

    def get_top_teams(self) -> Dict[str, int]:
        teams_dict = defaultdict(int)  # type: DefaultDict[str, int]
        for lineup in self.lineups:
            lineup_teams = {p.team for p in lineup}
            for team in lineup_teams:
                teams_dict[team] += 1
        return OrderedDict(sorted(teams_dict.items(), key=lambda t: -t[1]))

    def get_top_players(self) -> Dict[str, Dict[LineupPlayer, int]]:
        players = defaultdict(lambda: defaultdict(int))  # type: DefaultDict[str, DefaultDict[LineupPlayer, int]]
        for player in chain.from_iterable(self.lineups):
            players[player.full_name][player] += 1
        return OrderedDict(sorted(players.items(), key=lambda t: -sum(t[1].values())))  # type: ignore

    def print_report(self) -> None:
        top_teams = self.get_top_teams()
        if len(top_teams) > 1:
            print('Top Teams')
            for team, appearance in top_teams.items():
                print('  %s - %d' % (team, appearance))
            print('Used %d/%d\n' % (len(top_teams), len(self.optimizer.player_pool.available_teams)))
        print('Top Players')
        players_per_team = defaultdict(dict)  # type: DefaultDict[str, Dict[str, int]]
        top_players = self.get_top_players()
        total_players = len({player.full_name for player in self.optimizer.player_pool.all_players})
        replicated_players = Counter([player.full_name for player in self.optimizer.player_pool.all_players])
        for player_name, players in top_players.items():
            total = sum(players.values())
            players_per_team[list(players.keys())[0].team][player_name] = total
            by_positions = ''
            if replicated_players[player_name] > 1:
                by_positions = ','.join('%s-%d' % ('/'.join(player.positions), appearance)
                                        for player, appearance in players.items())
                by_positions = '(%s)' % by_positions
            print('  %s - %d %s' % (player_name, total, by_positions))
        print('Used %d/%d\n' % (len(top_players), total_players))
        if len(top_teams) > 1:
            print('Top Players Per Team')
            for team, team_players in sorted(players_per_team.items(), key=lambda t: -sum(t[1].values())):
                total_appearances = sum(team_players.values())
                team_players_str = ','.join('%s(%d)' % values for values in
                                            sorted(players_per_team[team].items(), key=lambda t: -t[1]))
                print('  %s(%d) - %s' % (team, total_appearances, team_players_str))

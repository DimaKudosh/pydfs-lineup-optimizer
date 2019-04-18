from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.lineup import Lineup, LineupPlayer


class BaseLineupPrinter(object):
    def print_lineup(self, lineup):
        # type: ('Lineup') -> str
        raise NotImplementedError


class LineupPrinter(BaseLineupPrinter):
    OUTPUT_FORMAT = '{0:>2}. {1:<5} {2:<30}{3:<6}{4:<15}{5:<9}{6:<8}{7:<10}\n'

    def _print_game_info(self, player):
        # type: ('LineupPlayer') -> str
        game_info = player.game_info
        if game_info:
            return '%s@%s' % (game_info.away_team, game_info.home_team)
        return ''

    def _print_player(self, index, player):
        # type: (int, 'LineupPlayer') -> str
        return self.OUTPUT_FORMAT.format(
            index,
            player.lineup_position,
            player.full_name,
            '/'.join(player.positions),
            player.team,
            self._print_game_info(player),
            round(player.fppg, 3),
            str(player.salary) + '$',
        )

    def print_lineup(self, lineup):
        res = ''
        for index, player in enumerate(lineup.players, start=1):
            res += self._print_player(index, player)
        res += '\nFantasy Points %.2f' % lineup.fantasy_points_projection
        res += '\nSalary %.2f\n' % lineup.salary_costs
        return res


class DropLowestLineupPrinter(LineupPrinter):
    def _print_player(self, index, player, is_dropped=False):
        return self.OUTPUT_FORMAT.format(
            index,
            player.lineup_position,
            '%s%s' % (player.full_name, '(DROPPED)' if is_dropped else ''),
            '/'.join(player.positions),
            player.team,
            self._print_game_info(player),
            round(player.fppg, 3),
            str(player.salary) + '$',
        )

    def print_lineup(self, lineup):
        res = ''
        lowest_fppg_player = sorted(lineup, key=lambda p: p.fppg)[0]
        for index, player in enumerate(lineup.players, start=1):
            res += self._print_player(index, player, is_dropped=lowest_fppg_player)
        res += 'Fantasy Points %.2f' % lineup.fantasy_points_projection
        res += '\nFantasy Points Without Dropped Player %.2f' % \
               (lineup.fantasy_points_projection - lowest_fppg_player.fppg)
        res += '\nSalary %.2f\n' % lineup.salary_costs
        return res


class IndividualSportLineupPrinter(LineupPrinter):
    def _print_player(self, index, player):
        return '{0:>2}. {1:<5} {2:<30}{3:<8}{4:<10}\n'.format(
            index,
            player.lineup_position,
            player.full_name,
            round(player.fppg, 3),
            str(player.salary) + '$',
        )

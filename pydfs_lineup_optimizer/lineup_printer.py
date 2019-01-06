from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.lineup import Lineup


class BaseLineupPrinter(object):
    def print_lineup(self, lineup):
        # type: ('Lineup') -> str
        raise NotImplementedError


class LineupPrinter(BaseLineupPrinter):
    def print_lineup(self, lineup):
        res = ''
        for index, player in enumerate(lineup.players, start=1):
            res += '{0:>2}. {1:<5} {2:<30}{3:<6}{4:<15}{5:<8}{6:<10}\n'.format(
                index,
                player.lineup_position,
                player.full_name,
                '/'.join(player.positions),
                player.team,
                round(player.fppg, 3),
                str(player.salary) + '$',
            )
        res += '\nFantasy Points %.2f' % lineup.fantasy_points_projection
        res += '\nSalary %.2f\n' % lineup.salary_costs
        return res


class DropLowestLineupPrinter(BaseLineupPrinter):
    def print_lineup(self, lineup):
        res = ''
        lowest_fppg_player = sorted(lineup, key=lambda player: player.fppg)[0]
        for index, player in enumerate(lineup.players, start=1):
            res += '{0:>2}. {1:<5} {2:<30}{3:<6}{4:<15}{5:<8}{6:<10}\n'.format(
                index,
                player.lineup_position,
                '%s%s' % (player.full_name, '(DROPPED)' if player == lowest_fppg_player else ''),
                '/'.join(player.positions),
                player.team,
                round(player.fppg, 3),
                str(player.salary) + '$',
            )
        res += 'Fantasy Points %.2f' % lineup.fantasy_points_projection
        res += '\nFantasy Points Without Dropped Player %.2f' % \
               (lineup.fantasy_points_projection - lowest_fppg_player.fppg)
        res += '\nSalary %.2f\n' % lineup.salary_costs
        return res

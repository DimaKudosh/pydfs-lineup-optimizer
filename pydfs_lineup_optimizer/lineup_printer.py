from typing import cast, TYPE_CHECKING


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.lineup import Lineup, LineupPlayer


class BaseLineupPrinter:
    def print_lineup(self, lineup: 'Lineup') -> str:
        raise NotImplementedError


class LineupPrinter(BaseLineupPrinter):
    OUTPUT_FORMAT = '{0:>2}. {1:<5} {2:<30}{3:<6}{4:<15}{5:<9}{6:<8}{7:<10}\n'

    def _print_game_info(self, player: 'LineupPlayer') -> str:
        game_info = player.game_info
        if game_info:
            return '%s@%s' % (game_info.away_team, game_info.home_team)
        return ''

    def _print_player(self, index: int, player: 'LineupPlayer') -> str:
        return self.OUTPUT_FORMAT.format(
            index,
            player.lineup_position,
            '%s%s' % (player.full_name, '(%s)' % player.roster_order if player.roster_order else ''),
            '/'.join(player.positions),
            player.team,
            self._print_game_info(player),
            round(player.fppg, 3),
            str(player.salary) + '$',
        )

    def _print_footer(self, lineup: 'Lineup') -> str:
        footer = 'Fantasy Points %.2f\n' % lineup.fantasy_points_projection
        footer += 'Salary %.2f\n' % lineup.salary_costs
        ownerships = [player.projected_ownership for player in lineup if player.projected_ownership]
        if ownerships:
            footer += 'Average Ownership %.1f%%\n' % (sum(ownerships) * 100 / len(ownerships))
        return footer

    def print_lineup(self, lineup):
        res = ''
        for index, player in enumerate(lineup.players, start=1):
            res += self._print_player(index, player)
        res += '\n'
        res += self._print_footer(lineup)
        return res


class DropLowestLineupPrinter(LineupPrinter):
    @staticmethod
    def _get_lowest_fppg_player(lineup: 'Lineup') -> 'LineupPlayer':
        return cast('LineupPlayer', sorted(lineup, key=lambda p: p.fppg)[0])

    def _print_player(self, index: int, player: 'LineupPlayer', is_dropped: bool = False) -> str:
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

    def _print_footer(self, lineup: 'Lineup') -> str:
        footer = super(DropLowestLineupPrinter, self)._print_footer(lineup)
        footer += 'Fantasy Points Without Dropped Player %.2f' % \
                  (lineup.fantasy_points_projection - self._get_lowest_fppg_player(lineup).fppg)
        return footer

    def print_lineup(self, lineup):
        res = ''
        lowest_fppg_player = self._get_lowest_fppg_player(lineup)
        for index, player in enumerate(lineup.players, start=1):
            res += self._print_player(index, player, is_dropped=player == lowest_fppg_player)
        res += '\n'
        res += self._print_footer(lineup)
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

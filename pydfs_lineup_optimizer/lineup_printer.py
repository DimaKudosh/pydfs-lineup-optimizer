from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.lineup import Lineup, LineupPlayer


class BaseLineupPrinter:
    def print_lineup(self, lineup: 'Lineup') -> str:
        raise NotImplementedError


class LineupPrinter(BaseLineupPrinter):
    OUTPUT_FORMAT = '{index:>2}. {lineup_position:<7} {name:<30}{positions:<6}{team:<15}{game:<9}' \
                    '{fppg:<15}{salary:<10}\n'

    def _print_game_info(self, player: 'LineupPlayer') -> str:
        game_info = player.game_info
        if game_info:
            return '%s@%s' % (game_info.away_team, game_info.home_team)
        return ''

    def _print_player(self, index: int, player: 'LineupPlayer') -> str:
        return self.OUTPUT_FORMAT.format(
            index=index,
            lineup_position=player.lineup_position,
            name='%s%s' % (player.full_name, '(%s)' % player.roster_order if player.roster_order else ''),
            positions='/'.join(player.original_positions),
            team=player.team,
            game=self._print_game_info(player),
            fppg=round(player.fppg, 3) if player.used_fppg is None or player.used_fppg == player.fppg else
            '%s(%s)' % (round(player.fppg, 3), round(player.used_fppg, 3)),
            salary=str(player.salary) + '$',
        )

    def _print_footer(self, lineup: 'Lineup') -> str:
        original_projection = lineup.fantasy_points_projection
        actual_projection = lineup.actual_fantasy_points_projection
        footer = 'Fantasy Points %.2f%s\n' % (
            original_projection, '(%.2f)' % actual_projection if actual_projection != original_projection else '')
        if lineup.salary_costs:
            footer += 'Salary %.2f\n' % lineup.salary_costs
        ownerships = [player.projected_ownership for player in lineup if player.projected_ownership is not None]
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


class IndividualSportLineupPrinter(LineupPrinter):
    OUTPUT_FORMAT = '{index:>2}. {lineup_position:<5} {name:<30}{fppg:<15}{salary:<10}\n'


class DraftKingTiersLineupPrinter(LineupPrinter):
    OUTPUT_FORMAT = '{index:>2}. {lineup_position:<5} {name:<30}{fppg:<15}\n'

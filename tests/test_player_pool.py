import unittest
from uuid import uuid4
from pydfs_lineup_optimizer import PlayerFilter
from pydfs_lineup_optimizer.sites import SitesRegistry
from pydfs_lineup_optimizer.constants import Site, Sport
from pydfs_lineup_optimizer.player_pool import PlayerPool
from pydfs_lineup_optimizer.player import Player
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException
from tests.utils import load_players


class PlayerPoolTestCase(unittest.TestCase):
    def setUp(self):
        self.players = load_players()
        self.settings = SitesRegistry.get_settings(Site.DRAFTKINGS, Sport.BASKETBALL)()
        self.player_pool = PlayerPool(settings=self.settings)
        self.player_pool.load_players(self.players)
        self.test_player = Player(player_id=str(uuid4()), first_name='Test', last_name='Test', team='Test',
                                  fppg=10, positions=['PG'], salary=100)

    def test_add_player(self):
        total_players = len(self.player_pool.all_players)
        self.player_pool.add_player(self.test_player)
        self.assertEqual(len(self.player_pool.all_players), total_players + 1)

    def test_lock_player(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        self.player_pool.lock_player(player)
        self.assertEqual(self.player_pool.locked_players, [player])
        self.assertEqual(self.player_pool.remaining_players, self.settings.get_total_players() - 1)
        self.assertEqual(self.player_pool.remaining_budget, self.settings.budget - player.salary)

    def test_lock_player_with_position(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        self.player_pool.lock_player(player, 'PG')
        self.assertEqual(self.player_pool.locked_players, [player])
        self.assertEqual(self.player_pool.remaining_players, self.settings.get_total_players() - 1)
        self.assertEqual(self.player_pool.remaining_budget, self.settings.budget - player.salary)
        player = self.player_pool.get_player_by_name('Ricky Rubio')
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.lock_player(player, 'PG')

    def test_lock_player_incorrect_position_name(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.lock_player(player, 'WRONG')

    def test_lock_player_to_wrong_position(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.lock_player(player, 'C')

    def test_lock_player_zero_max_exposure(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        player.max_exposure = 0
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.lock_player(player)

    def test_lock_player_twice(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        self.player_pool.lock_player(player)
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.lock_player(player)

    def test_lock_player_with_salary_bigger_than_budget(self):
        player = Player(str(uuid4()), 'Test', 'Test', ['PG'], 'DEN', 100000, 2)
        self.player_pool.add_player(player)
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.lock_player(player)

    def test_unlock_player(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        self.player_pool.lock_player(player)
        self.assertEqual(self.player_pool.locked_players, [player])
        self.player_pool.unlock_player(player)
        self.assertEqual(self.player_pool.locked_players, [])

    def test_unlock_not_locked_player(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.unlock_player(player)
        self.assertEqual(self.player_pool.locked_players, [])

    def test_exclude_player(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        self.player_pool.remove_player(player)
        self.assertNotIn(player, self.player_pool.filtered_players)

    def test_restore_player(self):
        player = self.player_pool.get_player_by_name('Russel Westbrook')
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.restore_player(player)

    def test_exclude_team(self):
        self.player_pool.add_player(self.test_player)
        self.player_pool.exclude_teams(['Test'])
        self.assertNotIn(self.test_player, self.player_pool.filtered_players)

    def test_get_player_by_id(self):
        player = self.player_pool.get_player_by_id('0000001')
        self.assertEqual(player.full_name, 'Russel Westbrook')

    def test_get_player_by_id_not_found(self):
        player = self.player_pool.get_player_by_id('zzzzzzz')
        self.assertIsNone(player)

    def test_get_player_by_name(self):
        self.player_pool.add_player(self.test_player)
        self.assertEqual(self.player_pool.get_player_by_name('Test Test'), self.test_player)

    def test_get_player_by_name_not_equal(self):
        self.player_pool.add_player(self.test_player)
        self.assertEqual(self.player_pool.get_player_by_name('Test  Tist'), self.test_player)

    def test_get_player_by_name_not_equal_disable_search(self):
        self.player_pool.search_threshold = None
        self.player_pool.add_player(self.test_player)
        self.assertIsNone(self.player_pool.get_player_by_name('Test  Tist'))

    def test_get_player_by_name_multiple_return_without_position(self):
        second_player = Player(player_id=str(uuid4()), first_name='Test', last_name='Test', team='Test',
                               fppg=10, positions=['SG'], salary=100)
        self.player_pool.extend_players([self.test_player, second_player])
        with self.assertRaises(LineupOptimizerException):
            self.player_pool.get_player_by_name('Test Test')

    def test_get_player_by_name_multiple_return(self):
        second_player = Player(player_id=str(uuid4()), first_name='Test', last_name='Test', team='Test',
                               fppg=10, positions=['SG'], salary=100)
        self.player_pool.extend_players([self.test_player, second_player])
        player = self.player_pool.get_player_by_name('Test Test', position='SG')
        self.assertEqual(player, second_player)

    def test_clean_player(self):
        self.player_pool.add_player(self.test_player)
        for player in (self.test_player, 'Test Test', 'Test'):
            self.assertEqual(self.test_player, self.player_pool._clean_player(player))

    def test_filter(self):
        self.player_pool.add_player(self.test_player)
        self.player_pool.add_filters(PlayerFilter(teams=['Test'], from_value=20))
        players = self.player_pool.filtered_players
        self.assertNotIn(self.test_player, players)
        self.assertEqual(len(self.players), len(players))

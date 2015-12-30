from pydfs_lineup_optimizer.settings import *


DFS_SITES = ["Yahoo", "FanDuel", "DraftKings", "FantasyDraft"]
DFS_SPORTS = ["Basketball", "Football", "Hockey"]
DFS_SETTINGS_DICT = {
    ("Yahoo", "Basketball"): YahooBasketballSettings,
    ("Yahoo", "Football"): YahooFootballSettings,
    ("Yahoo", "Hockey"): YahooHockeySettings,
    ("FanDuel", "Basketball"): FanDuelBasketballSettings,
    ("FanDuel", "Football"): FanDuelFootballSettings,
    ("DraftKings", "Basketball"): DraftKingsBasketballSettings,
    ("DraftKings", "Football"): DraftKingsFootballSettings,
    ("FantasyDraft", "Basketball"): FantasyDraftBasketballSettings,
    ("FantasyDraft", "Football"): FantasyDraftFootballSettings,
    ("FantasyDraft", "Hockey"): FantasyDraftHockeySettings,
}
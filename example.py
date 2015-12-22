from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer import settings

optimizer = LineupOptimizer(settings.FantasyDraftHockeySettings)
optimizer.load_players_from_CSV("FantasyDraftHockey.csv")
optimizer.optimize()
optimizer.print_lineup()

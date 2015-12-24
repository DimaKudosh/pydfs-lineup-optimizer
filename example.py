from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer import settings

optimizer = LineupOptimizer(settings.YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
optimizer.optimize()
optimizer.print_lineup()

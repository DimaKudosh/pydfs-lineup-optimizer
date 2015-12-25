from pydfs_lineup_optimizer import *

optimizer = LineupOptimizer(YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
optimizer.optimize()
optimizer.print_lineup()

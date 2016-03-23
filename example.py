from pydfs_lineup_optimizer import *

optimizer = LineupOptimizer(YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
lineup_generator = optimizer.optimize()
for lineup in lineup_generator:
    print(lineup)

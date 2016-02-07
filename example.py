from pydfs_lineup_optimizer import *

optimizer = LineupOptimizer(YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
a = optimizer.optimize()
for l in a:
    print(l)

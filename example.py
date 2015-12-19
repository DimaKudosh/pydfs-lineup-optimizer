from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer import settings


optimizer = LineupOptimizer(settings.YahooDailyFantasyBasketballSettings)
optimizer.load_players_from_CSV("11.csv")
optimizer.optimize()
optimizer.print_lineup()

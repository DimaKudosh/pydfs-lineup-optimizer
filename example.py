from pydfs_lineup_optimizer.lineup_optimizer import LineupOptimizer
from pydfs_lineup_optimizer import settings

optimizer = LineupOptimizer(settings.YahooDailyFantasyBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
optimizer.optimize(teams={'OKC': 4, 'HOU': 4})
optimizer.print_lineup()

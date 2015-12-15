from lineupoptimizer import LineupOptimizer
import settings


optimizer = LineupOptimizer(settings.YahooDailyFantasyBasketballSettings)
optimizer.load_players_from_CSV("nba_sample.csv")
optimizer.optimize()
optimizer.print_lineup()

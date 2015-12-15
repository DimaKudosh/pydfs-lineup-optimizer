from optimizer import Optimizer
import settings


optimizer = Optimizer(settings.YahooDailyFantasyBasketballSettings)
optimizer.load_players_from_CSV("nba_sample.csv")
optimizer.optimize()
optimizer.print_lineup()

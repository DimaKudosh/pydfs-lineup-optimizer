# PYDFS-LINEUP-OPTIMIZER
PYDFS-Lineup-optimizer is a tool for creating optimal lineups for daily fantasy sport. 

## Support
Now it's support following dfs sites:

League | Yahoo | Fanduel | DraftKings | FantasyDraft 
----- | ----- | ----- | ----- | ----- 
NFL | + | + | + | + 
NBA | + | + | + | + 
NHL | + | - | - | + 
MLB | - | - | - | - 

## Usage
Here is a example for evaluating optimal lineup for Yahoo fantasy NBA. It's loads players list from "yahoo-NBA.csv" and select best lineup with 4 Oklahoma City Thunder players.
```
optimizer = LineupOptimizer(settings.YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
optimizer.optimize(teams={'OKC': 4})
optimizer.print_lineup()
```

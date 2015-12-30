# PYDFS-LINEUP-OPTIMIZER
pydfs-lineup-optimizer is a tool for creating optimal lineups for daily fantasy sport. 

## Installation
To install pydfs-lineup-optimizer, simply:
```
$ pip install pydfs-lineup-optimizer
```

## Support
Now it's support following dfs sites:

League | Yahoo | Fanduel | DraftKings | FantasyDraft 
----- | ----- | ----- | ----- | ----- 
NFL | + | + | + | + 
NBA | + | + | + | + 
NHL | + | - | - | + 
MLB | - | - | - | - 

## Documentation
Documentation is available at https://github.com/DimaKudosh/pydfs-lineup-optimizer/wiki

## Example
Here is a example for evaluating optimal lineup for Yahoo fantasy NBA. It's loads players list from "yahoo-NBA.csv" and select best lineup with 4 Oklahoma City Thunder players.
```
optimizer = LineupOptimizer(settings.YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
optimizer.optimize(teams={'OKC': 4})
optimizer.print_lineup()
```
Also you can use simple standard GUI:
```
import pydfs_lineup_optimizer 
pydfs_lineup_optimizer.run_app()
```
# PYDFS-LINEUP-OPTIMIZER [![Build Status](https://travis-ci.org/DimaKudosh/pydfs-lineup-optimizer.svg?branch=master)](https://travis-ci.org/DimaKudosh/pydfs-lineup-optimizer)[![Coverage Status](https://coveralls.io/repos/github/DimaKudosh/pydfs-lineup-optimizer/badge.svg?branch=master)](https://coveralls.io/github/DimaKudosh/pydfs-lineup-optimizer?branch=master)
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
Here is a example for evaluating optimal lineup for Yahoo fantasy NBA. It's loads players list from "yahoo-NBA.csv" and select 10 best lineup with 4 Oklahoma City Thunder players.
```python
optimizer = LineupOptimizer(settings.YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
for lineup in optimizer.optimize(n=10, teams={'OKC': 4}):
    print(lineup)
```
Also you can use simple standard GUI:
```python
import pydfs_lineup_optimizer 
pydfs_lineup_optimizer.run_app()
```

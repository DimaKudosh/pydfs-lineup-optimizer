# PYDFS-LINEUP-OPTIMIZER [![Build Status](https://travis-ci.org/DimaKudosh/pydfs-lineup-optimizer.svg?branch=master)](https://travis-ci.org/DimaKudosh/pydfs-lineup-optimizer)[![Coverage Status](https://coveralls.io/repos/github/DimaKudosh/pydfs-lineup-optimizer/badge.svg?branch=master)](https://coveralls.io/github/DimaKudosh/pydfs-lineup-optimizer?branch=master)[![PyPI](https://img.shields.io/pypi/dm/Django.svg)](https://pypi.python.org/pypi/pydfs-lineup-optimizer/)[![PyPI](https://img.shields.io/pypi/pyversions/Django.svg)](https://pypi.python.org/pypi/pydfs-lineup-optimizer/)
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
Documentation is available at https://pydfs-lineup-optimizer.readthedocs.io/en/latest

## Example
Here is a example for evaluating optimal lineup for Yahoo fantasy NBA. It's loads players list from "yahoo-NBA.csv" and select 10 best lineup with 4 Oklahoma City Thunder players.
```python
optimizer = LineupOptimizer(settings.YahooBasketballSettings)
optimizer.load_players_from_CSV("yahoo-NBA.csv")
for lineup in optimizer.optimize(n=10, teams={'OKC': 4}):
    print(lineup)
```

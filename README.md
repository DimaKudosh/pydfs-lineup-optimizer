# PYDFS-LINEUP-OPTIMIZER [![Build Status](https://travis-ci.org/DimaKudosh/pydfs-lineup-optimizer.svg?branch=master)](https://travis-ci.org/DimaKudosh/pydfs-lineup-optimizer)[![Coverage Status](https://coveralls.io/repos/github/DimaKudosh/pydfs-lineup-optimizer/badge.svg?branch=master)](https://coveralls.io/github/DimaKudosh/pydfs-lineup-optimizer?branch=master)
pydfs-lineup-optimizer is a tool for creating optimal lineups for daily fantasy sport. 

## Installation
To install pydfs-lineup-optimizer, simply run:
```
$ pip install pydfs-lineup-optimizer
```

## Support
Now it supports following dfs sites:

League | DraftKings | FanDuel | FantasyDraft | Yahoo | FanBall | DraftKings Captain Mode | FanDuel Single Game | DraftKings Tiers |
------ | ---------- | ------- | ------------ | ----- | ------- | ----------------------- | ------------------- | ---------------- |
NFL    | +          | +       | +            | +     | +       | +                       | +                   | -                |
NBA    | +          | +       | +            | +     | -       | +                       | +                   | +                |
NHL    | +          | +       | +            | +     | -       | -                       | -                   | +                |
MLB    | +          | +       | +            | +     | -       | +                       | -                   | +                |
WNBA   | +          | +       | -            | -     | -       | +                       | -                   | -                |
Golf   | +          | +       | +            | +     | -       | -                       | -                   | -                |
Soccer | +          | -       | -            | +     | -       | +                       | -                   | -                |
CFL    | +          | -       | -            | -     | -       | -                       | -                   | -                |
LOL    | -          | +       | -            | -     | -       | +                       | +                   | -                |
MMA    | +          | +       | -            | -     | -       | -                       | -                   | -                |
NASCAR | +          | +       | -            | -     | -       | -                       | -                   | -                |
Tennis | +          | -       | -            | -     | -       | -                       | -                   | -                |
CSGO   | +          | -       | -            | -     | -       | -                       | -                   | -                |

## Documentation
Documentation is available at https://pydfs-lineup-optimizer.readthedocs.io/en/latest

## Example
Here is an example for evaluating optimal lineup for Yahoo fantasy NBA. It loads players list from "yahoo-NBA.csv" and select 10 best lineups.
```python
from pydfs_lineup_optimizer import Site, Sport, get_optimizer


optimizer = get_optimizer(Site.YAHOO, Sport.BASKETBALL)
optimizer.load_players_from_csv("yahoo-NBA.csv")
for lineup in optimizer.optimize(10):
    print(lineup)
```

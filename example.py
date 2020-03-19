#%%
from pydfs_lineup_optimizer import get_optimizer, Site, Sport, CSVLineupExporter
import warnings
from collections import OrderedDict
from itertools import chain
from math import ceil
from typing import FrozenSet, Type, Generator, Tuple, Union, Optional, List, Dict, Set, cast
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.solvers import Solver, PuLPSolver, SolverException
from pydfs_lineup_optimizer.exceptions import LineupOptimizerException, LineupOptimizerIncorrectTeamName, \
    LineupOptimizerIncorrectPositionName
from pydfs_lineup_optimizer.sites import SitesRegistry
from pydfs_lineup_optimizer.lineup_importer import CSVImporter
from pydfs_lineup_optimizer.settings import BaseSettings
from pydfs_lineup_optimizer.player import Player, LineupPlayer, GameInfo
from pydfs_lineup_optimizer.utils import ratio, link_players_with_positions, process_percents, get_remaining_positions
from pydfs_lineup_optimizer.rules import *
from pydfs_lineup_optimizer.stacks import BaseGroup, TeamStack, PositionsStack, BaseStack, Stack, PlayersGroup, Player
from collections import namedtuple
from datetime import datetime
from pytz import timezone
from typing import List, Optional
from pydfs_lineup_optimizer.utils import process_percents
from pydfs_lineup_optimizer.tz import get_timezone
import pandas as pd
import seaborn as sns
import numpy as np
import os
import matplotlib.pyplot as plt
import requests
from urllib.request import urlopen

#%%
#DraftStars AFL Lineup Generator
from pydfs_lineup_optimizer import Site, Sport, get_optimizer, CSVLineupExporter
import pandas as pd

optimizer = get_optimizer(Site.FANDUEL, Sport.FOOTBALL)
optimizer.load_players_from_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_ds_data.csv")

#player groups
group_1 = PlayersGroup([optimizer.get_player_by_name(name) for name in ('Kade Simpson', 'Sam Docherty')], max_exposure=0.1)
group_2 = PlayersGroup([optimizer.get_player_by_name(name) for name in ('Sam Docherty', 'Will Setterfield')], max_exposure=0.1)
group_3 = PlayersGroup([optimizer.get_player_by_name(name) for name in ('Sam Docherty', 'Nic Newman')], max_exposure=0.1)
optimizer.add_stack(Stack([group_1, group_2, group_3]))

x=50
lineups = CSVLineupExporter(optimizer.optimize(n=x,max_exposure=0.70,randomness=True))
lineups.export("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_ds_upload.csv")

# Datasets from folder Data
afl = pd.read_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_ds_upload.csv")

afl.head()
#Drop columns not required for exposure
afl_mod = afl.drop(['FPPG', 'Budget'] , axis='columns')
#Compute exposure
print(afl_mod.stack().value_counts()/x)

# %%
#Load AFl Data for Moneyball
from pydfs_lineup_optimizer import Site, Sport, get_optimizer, CSVLineupExporter
import pandas as pd

optimizer = get_optimizer(Site.DRAFTKINGS, Sport.FOOTBALL)
optimizer.load_players_from_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_moneyball_data_v1.csv")

x=50
lineups = CSVLineupExporter(optimizer.optimize(n=x,max_exposure=0.65,randomness=True))
lineups.export("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_moneyball_upload.csv")

# Datasets from folder Data
afl = pd.read_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_moneyball_upload.csv")
afl.head()
#Drop columns not required for exposure
afl_mod = afl.drop(['FPPG', 'Budget'] , axis='columns')
#Compute exposure
print(afl_mod.stack().value_counts()/x)



# %%
x=50
lineups = CSVLineupExporter(optimizer.optimize(n=x,max_exposure=0.65,randomness=True))
lineups.export("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_upload.csv")

# Datasets from folder Data
afl = pd.read_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_upload.csv")
afl.head()
#Drop columns not required for exposure
afl_mod = afl.drop(['FPPG', 'Budget'] , axis='columns')
#Compute exposure
print(afl_mod.stack().value_counts()/x)


# %%
afl = pd.read_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_upload.csv")
afl.head()
def afl_exposure (df):
    d = {}
    d['Count'] = df['FWD'].count()
    d['Count'] = df['FWD.1'].count()
    d['Count'] = df['MID'].count()
    d['Count'] = df['MID.1'].count()
    d['Count'] = df['MID.2'].count()
    d['Count'] = df['FLEX'].count()
    d['Count'] = df['DEF'].count()
    d['Count'] = df['DEF.1'].count()
    d['Count'] = df['RK'].count()
   
    return(pd.Series(d, index=[i for i in d]))

afl.groupby(['FWD']).apply(afl_exposure).round(4)
afl.groupby(['FWD.1']).apply(afl_exposure).round(4)
afl.groupby(['MID']).apply(afl_exposure).round(4)
afl.groupby(['MID.1']).apply(afl_exposure).round(4)
afl.groupby(['MID.2']).apply(afl_exposure).round(4)
afl.groupby(['FLEX']).apply(afl_exposure).round(4)
afl.groupby(['DEF']).apply(afl_exposure).round(4)
afl.groupby(['DEF.1']).apply(afl_exposure).round(4)
afl.groupby(['RK']).apply(afl_exposure).round(4)


# %%

#%%

player_1 = optimizer.get_player_by_name('Jack Martin')
player_2 = optimizer.get_player_by_name('Devonte\' Graham (133996)')
player_3 = optimizer.get_player_by_name('Dorian Finney-Smith (12563)')
player_4 = optimizer.get_player_by_name('Jordan McRae (8678)')
player_5 = optimizer.get_player_by_name('Luka Doncic (133960)')
player_6 = optimizer.get_player_by_name('Josh Richardson (8853)')
player_7 = optimizer.get_player_by_name('Caleb Martin (251446)')
player_8 = optimizer.get_player_by_name(' Cody Zeller (8821)')
player_9 = optimizer.get_player_by_name(' Cody Martin (251482)')
player_10 = optimizer.get_player_by_name('Cam Reddish (251432)')
player_11 = optimizer.get_player_by_name('Terry Rozier (8791)')
player_12 = optimizer.get_player_by_name('Rudy Gobert (8492)')
player_13 = optimizer.get_player_by_name('Harrison Barnes (8786)')
player_14 = optimizer.get_player_by_name('De\'Andre Hunter (251521)')
player_15 = optimizer.get_player_by_name('Donovan Mitchell (15661)')
player_16 = optimizer.get_player_by_name('Jae Crowder (8810)')

player_1.max_exposure = 0.20
player_2.min_exposure = 0.50
player_3.max_exposure = 0.00
player_4.max_exposure = 0.05
player_5.max_exposure = 0.15
player_6.max_exposure = 0.10
player_7.min_exposure = 0.02
player_8.max_exposure = 0.06
player_9.min_exposure = 0.02
player_10.max_exposure = 0.10
player_11.max_exposure = 0.00
player_12.max_exposure = 0.00
player_13.max_exposure = 0.10
player_14.max_exposure = 0.12
player_15.max_exposure = 0.20
player_16.max_exposure = 0.10


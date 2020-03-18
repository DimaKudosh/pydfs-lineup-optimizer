#%%
from pydfs_lineup_optimizer import Site, Sport, get_optimizer
import pandas as pd

optimizer = get_optimizer(Site.FANDUEL, Sport.HOCKEY)
optimizer.load_players_from_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_data.csv")
player = pd.read_csv ("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/afl_data.csv")
player.head()
lineup_generator = optimizer.optimize(20)
for lineup in lineup_generator:
    print(lineup)



# %%

from pydfs_lineup_optimizer import Site, Sport, get_optimizer


optimizer = get_optimizer(Site.moneyball, Sport.FOOTBALL)
optimizer.load_players_from_csv("/Users/raymond.huynh/Desktop/python/Ray_Python/data/fantasy/nrl_mock.csv")
lineup_generator = optimizer.optimize(10)
for lineup in lineup_generator:
    print(lineup)


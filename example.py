from pydfs_lineup_optimizer import Site, Sport, get_optimizer, ProjectionFilter


optimizer = get_optimizer(Site.YAHOO, Sport.BASKETBALL)
optimizer.load_players_from_csv("yahoo-NBA.csv")
player_pool = optimizer.player_pool
player_pool.add_filters(
    ProjectionFilter(from_projection=20, position='QB'),
    ProjectionFilter(from_projection=10, position='TE'),
)
lineup_generator = optimizer.optimize(10)
for lineup in lineup_generator:
    print(lineup)
optimizer.print_statistic()

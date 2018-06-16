.. _pydfs-lineup-optimizer-performance-and-optimization:


Performance and Optimization
============================

Sometimes optimization process takes a lot of time to generate single lineup.
It usually happens in mlb and nfl because all teams plays in same day and each team has a lot of players and total
number of players used in optimization is >500. In this case a good approach is to remove from optimization players with
small fppg value and big salary.

.. code-block:: python

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL)
    optimizer.load_players_from_CSV('dk_mlb.csv')
    for player in optimizer.players:
        if player.efficiency == 0:
            optimizer.remove_player(player)
    for lineup in optimizer.optimize(10):
        print(lineup)

.. _pydfs-lineup-optimizer-performance-and-optimization:


Performance and Optimization
============================

Sometimes optimization process takes a lot of time to generate single lineup.
It usually happens in mlb and nfl because all teams plays in same day and each team has a lot of players and total
number of players used in optimization is >500. In this case a good approach is to remove from optimization players with
small fppg value and big salary.

.. code-block:: python

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL)
    optimizer.load_players_from_csv('dk_mlb.csv')
    for player in optimizer.players:
        if player.efficiency == 0:
            optimizer.remove_player(player)
    for lineup in optimizer.optimize(10):
        print(lineup)

Optimizer parameters tuning
---------------------------

For some special cases with a lot of different constraints you can try to tune solver parameters.
`pydfs-lineup-optimizer` uses `PuLP` library for solving optimization problem, by default it uses CBC solver so you can
try to change default parameters. You can find list of available parameters `here
<https://www.gams.com/latest/docs/S_CBC.html>`_.
This is example of tuning parameters:

.. code-block:: python

    from pulp.solvers import PULP_CBC_CMD
    from pydfs_lineup_optimizer import get_optimizer, Site, Sport
    from pydfs_lineup_optimizer.solvers.pulp_solver import PuLPSolver


    class CustomPuLPSolver(PuLPSolver):
        LP_SOLVER = PULP_CBC_CMD(threads=8, options=['preprocess off'])


    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL, solver=CustomPuLPSolver)

You can try to change solver as well for any solver that `PuLP` support: glpk, cplex, gurobi etc.

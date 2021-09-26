.. _pydfs-lineup-optimizer-performance-and-optimization:


Performance and Optimization
============================

Solvers
-------

By default, the optimizer uses `pulp <https://coin-or.github.io/pulp/index.html>`_ library under the hood with a default solver that is free but slow.
You can change it to another solver that pulp supports.
Here is an example of how to change the default solver for GLPK solver:

.. code-block:: python

    # install glpk: https://www.gnu.org/software/glpk/
    from pulp import GLPK_CMD  # You can find names of other solvers in pulp docs
    from pydfs_lineup_optimizer.solvers import PuLPSolver

    class GLPKPuLPSolver(PuLPSolver):
        LP_SOLVER = GLPK_CMD(path='<path to installed glpk solver>', msg=False)

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL, solver=GLPKPuLPSolver)

Also, the library supports another solver library: `mip <https://www.python-mip.com/>`_.
It can be faster in some cases, especially if you are using pypy (`benchmark <https://docs.python-mip.com/en/latest/bench.html>`_).
For you using mip you should install it via pip: pip install mip.
After that you can replace pulp:

.. code-block:: python

    from pydfs_lineup_optimizer.solvers.mip_solver import MIPSolver

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL, solver=MIPSolver)

Decrease solving complexity
---------------------------

Sometimes optimization process takes a lot of time to generate a single lineup.
It usually happens in mlb and nfl because all teams play on the same day and each team has a lot of players and the total
number of players used in optimization is >100. In this case, a good approach is to remove from optimization players with
small fppg value and a big salary.

.. code-block:: python

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASEBALL)
    optimizer.load_players_from_csv('dk_mlb.csv')
    optimizer.player_pool.add_filters(
        PlayerFilter(from_value=5),  # use only players with points >= 5
        PlayerFilter(from_value=2, filter_by='efficiency'),  # and efficiency(points/salary) >= 2
        PlayerFilter(from_value=2000, filter_by='salary'),  # and salary >= 3000
    )
    optimizer.player_pool.exclude_teams(['Seattle Mariners'])
    for lineup in optimizer.optimize(100):
        print(lineup)

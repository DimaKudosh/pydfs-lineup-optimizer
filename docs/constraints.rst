.. _pydfs-lineup-optimizer-usage:


Constraints
===========

**pydfs-lineup-optimizer** has ability to set custom constraints for optimizer. It has following constraints:

- Number of players from same team.
- Positions for same team.
- Number of specific positions.
- Minimum salary cap.

For setting number of players from same team constraint you must call `set_players_from_one_team` method of optimizer.
It accepts dict where key is a team name and value is number of players for this team.

.. code-block:: python

    optimizer.set_players_from_one_team({'OKC': 4})

For setting positions for same team you must call `set_positions_for_same_team` method of optimizer.
It accepts list with positions that must be selected from one team.

.. code-block:: python

    optimizer.set_positions_for_same_team(['QB', 'WR', 'WR'])

For setting specific players positions for multi-position slots optimizer has `set_players_with_same_position` method.
It accepts dict where key is a position name and value is number of players with this position.

.. code-block:: python

    optimizer.set_players_with_same_position({'PG': 3})

.. note::

   Positions constraint hasn't effect for dfs sites without multi-position slots(G, UTIL, etc.)

You can set minimum salaries cap using `set_min_salary_cap` method. If you set min salary cap greater than maximun budget `LineupOptimizerException` will be raised.

.. code-block:: python

    optimizer.set_min_salary_cap(49000)

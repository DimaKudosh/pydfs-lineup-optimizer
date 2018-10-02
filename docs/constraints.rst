.. _pydfs-lineup-optimizer-constraints:


Constraints
===========

**pydfs-lineup-optimizer** has ability to set custom constraints for optimizer. It has following constraints:

- Number of players from same team.
- Positions for same team.
- Number of specific positions.
- Minimum salary cap.
- Maximum repeating players.
- Ownership projection constraint.

Number of players from same team
--------------------------------
For setting number of players from same team constraint you should call `set_players_from_one_team` method of optimizer.
It accepts dict where key is a team name and value is number of players for this team.

.. code-block:: python

    optimizer.set_players_from_one_team({'OKC': 4})

Positions for same team
-----------------------
For setting positions for same team you should call `set_positions_for_same_team` method of optimizer.
It accepts list with positions that must be selected from one team.

.. code-block:: python

    optimizer.set_positions_for_same_team(['QB', 'WR', 'WR'])


Number of specific positions
----------------------------
For setting specific players positions for multi-position slots optimizer has `set_players_with_same_position` method.
It accepts dict where key is a position name and value is number of players with this position.

.. code-block:: python

    optimizer.set_players_with_same_position({'PG': 2})

.. note::

   Positions constraint hasn't effect for dfs sites without multi-position slots(G, UTIL, etc.)


Minimum salary cap
------------------
You can set minimum salaries cap using `set_min_salary_cap` method. If you set min salary cap greater than maximum budget `LineupOptimizerException` will be raised.

.. code-block:: python

    optimizer.set_min_salary_cap(49000)

Maximum repeating players
-------------------------
If you want to make more random lineups you can use `set_max_repeating_players` method.
This method adds constraint that restrict players combinations that used in previous lineup.
It accepts only one argument: number of maximum repeating players.

.. code-block:: python

    optimizer.set_max_repeating_players(5)

Ownership projections constraint
--------------------------------
If you want to avoid a lot of highly-owned players in your lineups you can use `set_projected_ownership` method.
This method working with player `projected_ownership` field, so if you want to use this constraint you should set this
field for players before creating lineups. Optimizer's `set_projected_ownership` method accepts 2 arguments `min_projected_ownership`
and `max_projected_ownership` that are max/min percent of average ownership in generated lineup.

.. code-block:: python

    for player in optimizer.players:
        player.projected_ownership = get_projected_ownership(player)  # User defined function for getting ownership percent
    optimizer.set_projected_ownership(max_projected_ownership=0.6)

If you don't specify `projected_ownership` for some players this players will not used in calculating lineup average
ownership, but they can appear in result lineup.
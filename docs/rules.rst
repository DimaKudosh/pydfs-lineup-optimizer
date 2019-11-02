.. _pydfs-lineup-optimizer-constraints:


Rules
=====

**pydfs-lineup-optimizer** has ability to set custom rules for optimizer. It has following constraints:

- Number of players from same team.
- Positions for same team.
- Number of specific positions.
- Minimum salary cap.
- Maximum repeating players.
- Ownership projection constraint.
- Team stacking
- Restrict players from opposing team
- Restrict players from same team
- Force players from opposing team
- Spacing for positions
- Teams exposures
- Total teams

Number of players from same team
--------------------------------
For setting number of players from same team rule you should call `set_players_from_one_team` method of optimizer.
It accepts dict where key is a team name and value is number of players for this team.

.. code-block:: python

    optimizer.set_players_from_one_team({'OKC': 4})

Positions for same team
-----------------------
For setting positions for same team you should use `set_positions_for_same_team` method of optimizer.
It accepts list with positions that must be selected from one team. You can specify multiple positions stacks as well.

.. code-block:: python

    optimizer.set_positions_for_same_team(['QB', 'WR', 'WR'])
    optimizer.set_positions_for_same_team(['QB', 'WR', ('WR', 'TE')])
    optimizer.set_positions_for_same_team(['WR', 'WR', 'WR'], ['RB', 'RB'])


Number of specific positions
----------------------------
For setting specific players positions for multi-position slots optimizer has `set_players_with_same_position` method.
It accepts dict where key is a position name and value is number of players with this position.

.. code-block:: python

    optimizer.set_players_with_same_position({'PG': 2})

.. note::

   Positions rule hasn't effect for dfs sites without multi-position slots(G, UTIL, etc.)


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
This method working with player `projected_ownership` field, so if you want to use this rule you should set this
field for players before creating lineups. Optimizer's `set_projected_ownership` method accepts 2 arguments `min_projected_ownership`
and `max_projected_ownership` that are max/min percent of average ownership in generated lineup.

.. code-block:: python

    for player in optimizer.players:
        player.projected_ownership = get_projected_ownership(player)  # User defined function for getting ownership percent
    optimizer.set_projected_ownership(max_projected_ownership=0.6)

If you don't specify `projected_ownership` for some players this players will not used in calculating lineup average
ownership, but they can appear in result lineup.

Teams stacking
--------------
You can set how many players from same team will be in lineup, for this you can use `set_team_stacking` method.
It accepts list with integers, each integer represents minimum number of players from same team, so you can stack multiple teams if you want.
Also you can specify positions used in stack if you want.

.. code-block:: python

    optimizer.set_team_stacking([3, 3])
    optimizer.set_team_stacking([3, 3], for_positions=['1B', '2B', '3B', 'C', 'SS', 'OF'])

Restrict players from opposing team
-----------------------------------
In some cases you would want to restrict creating of lineup with players from opposing teams,
for example prevent of pitchers and hitters from same game. For this you can use `restrict_positions_for_opposing_team`
method of optimizer, it accepts 2 arguments with list of positions for one team and list of positions for another.

.. code-block:: python

    optimizer.restrict_positions_for_opposing_team(['P'], ['1B', '2B', '3B'])

.. note::

    This constraint works only when players has information about upcoming game and their opponents,
    in other case `LineupOptimizerException` will be raised. So it will not work in FantasyDraft
    (because they doesn't provide information about opponents) and if you write your custom players importer and
    don't pass `game_info` parameter in players constructors.

Restrict players from same team
-------------------------------
In some cases you would want to restrict creating of lineup with players from same team,
for example prevent of 2 RB from same team. For this you can use `restrict_positions_for_same_team`
method of optimizer, it takes tuples with 2 positions.

.. code-block:: python

    optimizer.restrict_positions_for_same_team(('RB', 'RB'))
    optimizer.restrict_positions_for_same_team(('QB', 'DST'), ('RB', 'DST'))


Force players from opposing team
--------------------------------
If you want to force players from opposing team
you can use `force_positions_for_opposing_team` rule,
it takes tuples with 2 positions.

.. code-block:: python

    optimizer.force_positions_for_opposing_team(('QB', 'WR'))


Spacing for positions
---------------------

For some sports like baseball it can be useful to select players based on lineup ordering (batters hit order).
This rule allow you to select players close to each other according to lineup order.
For example if you want to restrict optimizer to select players within specific range.

.. code-block:: python

    optimizer.set_spacing_for_positions(['1B', '2B', '3B'], 3)  # This will select players close to each other in range of 3 spots. 1-3, 2-4, 3-5 etc.

.. note::

    Because dfs sites doesn't provide information about batters hit order you should add additional column "Roster Order" where you can set this order,
    or specify it in Player objects using roster_order attribute. In other case this rule will be ignored.

Teams exposures
---------------

This rule adds maximum exposures for teams used in stacking.
It only works with `set_team_stacking` or `set_positions_for_same_team` rules.

.. code-block:: python

    optimizer.set_teams_max_exposure({'BOS': 0.3, 'LAL': 0.4})
    # Set same max exposures for all teams
    optimizer.set_teams_max_exposure({team: 0.2 for team in optimizer.available_teams})

Total teams
-----------

It's also possible to set exact number of teams that will be presented in generated lineups,
you can set it using `set_total_teams` method.

.. code-block:: python

    optimizer.set_total_teams(4)

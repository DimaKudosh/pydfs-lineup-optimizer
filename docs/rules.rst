.. _pydfs-lineup-optimizer-constraints:


Rules
=====

**pydfs-lineup-optimizer** allows you to set custom rules for optimizer. It has following rules:

- Number of players from same team.
- Number of specific positions.
- Minimum salary cap.
- Maximum repeating players.
- Ownership projection constraint.
- Restrict players from opposing team
- Restrict players from same team
- Force players from opposing team
- Spacing for positions
- Total teams
- Minimum starters
- Stacking rules

Number of players from same team
--------------------------------
For setting number of players from same team rule you should call `set_players_from_one_team` method of optimizer.
It accepts dict where key is a team name and value is number of players for this team.

.. code-block:: python

    optimizer.set_players_from_one_team({'OKC': 4})


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

Restrict players from opposing team
-----------------------------------
In some cases you would want to restrict creating of lineup with players from opposing teams,
for example prevent of pitchers and hitters from same game. For this you can use `restrict_positions_for_opposing_team`
method of optimizer, it accepts 2 arguments with list of positions for one team and list of positions for another and
optional argument that specify max allowed players from opposing team. By default this argument is 0 but you can change
it in some cases. For example if you participate in tournament with a few games.


.. code-block:: python

    optimizer.restrict_positions_for_opposing_team(['P'], ['C', 'SS', 'OF', '1B', '2B', '3B'])
    optimizer.restrict_positions_for_opposing_team(['P'], ['C', 'SS', 'OF', '1B', '2B', '3B'], 1)  # 1 hitter from opposing team is allowed

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

Total teams
-----------

It's also possible to set exact number of teams that will be presented in generated lineups,
you can set it using `set_total_teams` method.

.. code-block:: python

    optimizer.set_total_teams(4)

Minimum starters
----------------

You can force optimizer to choose minimum number of starters using `set_min_starters` method.
For marking player as starter you can set `is_confirmed_starter` attribute of Player object to True or
add `Confirmed Starter` column to csv.

.. code-block:: python

    optimizer.set_min_starters(4)


Stacking
========

**pydfs-lineup-optimizer** allows you to set stacking for lineups based on different rules.
For this you should pass your stack object to `add_stack` method of optimizer.
Here is a list of available types of stacks:

Team stack
----------
You can set how many players from same team will be in lineup, for this you can use `TeamStack`.
Here are examples of using it:

.. code-block:: python

    optimizer.add_stack(TeamStack(3))  # stack 3 players
    optimizer.add_stack(TeamStack(3, for_teams=['NE', 'BAL', 'KC']))  # stack 3 players from any of specified teams
    optimizer.add_stack(TeamStack(3, for_positions=['QB', 'WR', 'TE']))  # stack 3 players with any of specified positions
    optimizer.add_stack(TeamStack(3, spacing=2))  # stack 3 players close to each other in range of 2 spots.
    optimizer.add_stack(TeamStack(3, max_exposure=0.5))  # stack 3 players from same team with 0.5 exposure for all team stacks
    optimizer.add_stack(TeamStack(3, max_exposure=0.5, max_exposure_per_team={'MIA': 0.6}))  # stack 3 players from same team with 0.5 exposure for all team stacks and 0.6 exposure for MIA

Positions stack
---------------
You also can add stack with known list of positions for players used in stack.
Here are examples of using it:

.. code-block:: python

    optimizer.add_stack(PositionsStack(['QB', 'WR']))  # stack QB and WR from same team
    optimizer.add_stack(PositionsStack(['QB', ('WR', 'TE')]))  # stack QB and WR or TE from same team
    optimizer.add_stack(PositionsStack(['QB', 'WR'], for_teams=['NO', 'MIA', 'KC']))  # stack QB and WR for one of provided teams
    optimizer.add_stack(PositionsStack(['QB', 'WR'], max_exposure=0.5))  # stack QB and WR with 0.5 exposure for all team stacks
    optimizer.add_stack(PositionsStack(['QB', 'WR'], max_exposure=0.5, max_exposure_per_team={'MIA': 0.6}))  # stack QB and WR  with 0.5 exposure for all team stacks and 0.6 exposure for MIA

Custom stack
------------
You can create your custom stacks as well. Here is example of creating custom stack so optimizer will
create lineups with Rodgers/Adams or Brees/Thomas duos with 0.5 exposure:

.. code-block:: python

    rodgers_adams_group = PlayersGroup([optimizer.get_player_by_name(name) for name in ('Aaron Rodgers', 'Davante Adams')], max_exposure=0.5)
    brees_thomas_group = PlayersGroup([optimizer.get_player_by_name(name) for name in ('Drew Brees', 'Michael Thomas')], max_exposure=0.5)
    optimizer.add_stack(Stack([rodgers_adams_group, brees_thomas_group]))

Group players
-------------
You can group players in your lineups for this you can use `add_players_group` method of optimizer.
Here is an example:

.. code-block:: python

    group = PlayersGroup([optimizer.get_player_by_name(name) for name in ('LeBron James', 'Anthony Davis')])
    optimizer.add_players_group(group)

You can use this method for ungrouping players as well. In this example maximum one player will be in lineup.

.. code-block:: python

    group = PlayersGroup([optimizer.get_player_by_name(name) for name in ('LeBron James', 'Anthony Davis')], max_from_group=1)
    optimizer.add_players_group(group)

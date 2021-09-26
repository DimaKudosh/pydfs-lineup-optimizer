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
- Teams exposures
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
        player.projected_ownership = 0.1
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

You can control the total number of teams used in lineups using `set_total_teams` method.

.. code-block:: python

    optimizer.set_total_teams(min_teams=4)  # At least 4 teams should be in the lineup
    optimizer.set_total_teams(max_teams=6)  # Maximum 6 teams should be in the lineup
    optimizer.set_total_teams(min_teams=5, max_teams=6)  # 5 or 6 teams should be in the lineup
    optimizer.set_total_teams(min_teams=5, max_teams=5)  # Exact 5 teams should be in the lineup

Minimum starters
----------------

You can force optimizer to choose minimum number of starters using `set_min_starters` method.
For marking player as starter you can set `is_confirmed_starter` attribute of Player object to True or
add `Confirmed Starter` column to csv.

.. code-block:: python

    optimizer.set_min_starters(4)

Teams exposures
---------------

You can set max exposures for each team it means that players from teams can be used only in a limited number of lineups.
The team counted as used in the lineup if at least one player from it is in the lineup.

.. code-block:: python

    optimizer.set_teams_max_exposures(0.5)  # Set 0.5 exposure for all teams
    optimizer.set_teams_max_exposures(0.5, exposures_by_team={'NYY': 0.8})  # Set 0.5 exposure for all teams except NYY and 0.8 exposure for NYY
    optimizer.set_teams_max_exposures(exposures_by_team={'NYY': 0.8})  # Set 0.5 exposure only for NYY
    optimizer.set_teams_max_exposures(exposures_by_team={'NYY': 0.5, 'NYM': 0.5}, exposure_strategy=AfterEachExposureStrategy)  # Use another exposure strategy


Stacking
========

**pydfs-lineup-optimizer** allows you to set stacking for lineups based on different rules.
For this you should pass your stack object to `add_stack` method of optimizer.
Here is a list of available types of stacks:

Team stack
----------
You can set how many players from the same team will be in the lineup, for this you can use `TeamStack`.
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
You also can add a stack with a known list of positions for players used in the stack.
Here are examples of using it:

.. code-block:: python

    optimizer.add_stack(PositionsStack(['QB', 'WR']))  # stack QB and WR from same team
    optimizer.add_stack(PositionsStack(['QB', ('WR', 'TE')]))  # stack QB and WR or TE from same team
    optimizer.add_stack(PositionsStack(['QB', 'WR'], for_teams=['NO', 'MIA', 'KC']))  # stack QB and WR for one of provided teams
    optimizer.add_stack(PositionsStack(['QB', 'WR'], max_exposure=0.5))  # stack QB and WR with 0.5 exposure for all team stacks
    optimizer.add_stack(PositionsStack(['QB', 'WR'], max_exposure=0.5, max_exposure_per_team={'MIA': 0.6}))  # stack QB and WR  with 0.5 exposure for all team stacks and 0.6 exposure for MIA

Game stack
---------------
You can set how many players from the same game will be in the lineup, for this you can use `GameStack`.

.. code-block:: python

    optimizer.add_stack(GameStack(3))  # stack 3 players from the same game
    optimizer.add_stack(GameStack(5, min_from_team=2))  # stack 5 players from the same game, 3 from one team and 2 from another

Custom stack
------------
You can create your custom stacks as well. Here is example of creating custom stack so optimizer will
create lineups with Rodgers/Adams or Brees/Thomas duos with 0.5 exposure:

.. code-block:: python

    rodgers_adams_group = PlayersGroup(optimizer.player_pool.get_players('Aaron Rodgers', 'Davante Adams'), max_exposure=0.5)
    brees_thomas_group = PlayersGroup(optimizer.player_pool.get_players('Drew Brees', 'Michael Thomas'), max_exposure=0.5)
    optimizer.add_stack(Stack([rodgers_adams_group, brees_thomas_group]))

Group players
-------------
You can group players in your lineups using `add_players_group` method of the optimizer.
Here is an example:

.. code-block:: python

    group = PlayersGroup(optimizer.player_pool.get_players('LeBron James', 'Anthony Davis'))
    optimizer.add_players_group(group)

You can use this method for ungrouping players as well. In this example maximum of one player will be in the lineup.

.. code-block:: python

    group = PlayersGroup(optimizer.player_pool.get_players('LeBron James', 'Anthony Davis'), max_from_group=1)
    optimizer.add_players_group(group)

Also you can apply these groups conditionally based on another player selection.
In the example below one of Travis Kelce or Tyreek Hill will be added to the lineup only with Patrick Mahomes or none of them will be added to the lineup.
You can allow generating lineups with the provided group when the dependent player is not in the lineup,
for this you can set optional argument `strict_depend` to `False`.

.. code-block:: python

    group = PlayersGroup(
        optimizer.player_pool.get_players('Tyreek Hill', 'Travis Kelce'),
        max_from_group=1,
        depends_on=optimizer.player_pool.get_player_by_name('Patrick Mahomes'),
        strict_depend=False, # if you want to generate lineups with Hill/Kelce but without Mahomes
    )
    optimizer.add_players_group(group)

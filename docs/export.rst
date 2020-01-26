.. _pydfs-lineup-optimizer-export:


Export lineups
==============

You can export lineups into a csv file. **pydfs-lineup-optimizer** has helper class for this called `CSVLineupExporter`.
You should pass iterable with lineups to constructor and then call `export` method with filename argument.

.. code-block:: python

    from pydfs_lineup_optimizer import get_optimizer, Site, Sport, CSVLineupExporter

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
    optimizer.load_players_from_csv("players.csv")
    exporter = CSVLineupExporter(optimizer.optimize(10))
    exporter.export('result.csv')

Exported file has following format.

+--------------------+------------+--------------------+--------+------+
| Position 1         | ...        | Position n         | Budget | FPPG |
+====================+============+====================+========+======+
| Player Name 1 (id) | ...        | Player Name n (id) | 200    | 190  |
+--------------------+------------+--------------------+--------+------+
| Player Name 1 (id) | ...        | Player Name n (id) | 200    | 188  |
+--------------------+------------+--------------------+--------+------+
| ...                | ...        | ...                | ...    | ...  |
+--------------------+------------+--------------------+--------+------+
| Player Name 1 (id) | ...        | Player Name n (id) | 199    | 170  |
+--------------------+------------+--------------------+--------+------+

If you want to display another information for player you can pass your own function for rendering player data as second argument to export.

.. code-block:: python

    exporter.export('result.csv', lambda p: p.id)

.. note::

    Fantasy Draft has special requirements for import file so if you want to use export feature for Fantasy Draft
    you should download players list from Lineups page then use `FantasyDraftCSVLineupExporter` instead of `CSVLineupExporter`
    and pass file with players to export function so export will append generate lineups.

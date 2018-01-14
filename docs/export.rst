.. _pydfs-lineup-optimizer-usage:


Export lineups
==============

You can export lineups into a csv file. **pydfs-lineup-optimizer** has helper class for this called `CSVLineupExporter`.
You must pass iterable with lineups to constructor and then call `export` method with filename argument.

.. code-block:: python

    from pydfs_lineup_optimizer import get_optimizer, Site, Sport, CSVLineupExporter

    optimizer = get_optimizer(Site.DRAFTKINGS, Sport.BASKETBALL)
    optimizer.load_players_from_CSV("players.csv")
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

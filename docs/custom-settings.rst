.. _pydfs-lineup-optimizer-custom-settings:


Custom Settings
===============

Using Custom Settings
---------------------

You can create custom settings for new sport or dfs site.
For this, you should create a settings class inherited from `BaseSettings` class and provide all necessary information according to the rules you want.

.. code-block:: python

    from pydfs_lineup_optimizer import LineupOptimizer
    from pydfs_lineup_optimizer.settings import BaseSettings, LineupPosition

    class CustomSettings(BaseSettings):
        site = 'Site Name'
        sport = 'Sport Name'
        budget = 100  # budget you want to use
        max_from_one_team = None  # if needed
        min_teams = None  # if needed
        min_games = None  # if needed
        csv_importer = None  # If player will be imported using load_players_from_csv method
        positions = [  # list of all positions
            LineupPosition('G', ('PG', 'SG')),  # First argument is name of position in lineup,
                                                # second is allowed player positions for this lineup position
            # etc
        ]

    optimizer = LineupOptimizer(CustomSettings)

__version__ = "0.2"

from .player import Player
from .exceptions import LineupOptimizerException
from .settings import *
from .lineup_optimizer import LineupOptimizer
from .app.app import run


def run_app():
    run()

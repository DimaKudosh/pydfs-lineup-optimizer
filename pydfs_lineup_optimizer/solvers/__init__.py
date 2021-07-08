import os
from typing import Type
from pydfs_lineup_optimizer.solvers.base import Solver
from pydfs_lineup_optimizer.solvers.pulp_solver import PuLPSolver
from pydfs_lineup_optimizer.solvers.constants import SolverSign
from pydfs_lineup_optimizer.solvers.exceptions import SolverException, SolverInfeasibleSolutionException


__all__ = ['Solver', 'PuLPSolver', 'SolverSign', 'SolverException', 'SolverInfeasibleSolutionException',
           'get_default_solver']


def get_default_solver() -> Type[Solver]:
    solver_backend = os.environ.get('SOLVER_BACKEND')
    if solver_backend is None:
        return PuLPSolver
    solver_backend_name = solver_backend.lower()
    if solver_backend_name == 'pulp':
        return PuLPSolver
    elif solver_backend_name == 'mip':
        from pydfs_lineup_optimizer.solvers.mip_solver import MIPSolver
        return MIPSolver
    raise ValueError('Unknown solver backend: %s' % solver_backend)

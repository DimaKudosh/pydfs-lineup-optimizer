from typing import List


class SolverException(Exception):
    pass


class SolverInfeasibleSolutionException(SolverException):
    def __init__(self, invalid_constraints: List[str]):
        self.invalid_constraints = invalid_constraints

    def get_user_defined_constraints(self) -> List[str]:
        return [name for name in self.invalid_constraints if not name.startswith('_')]

from typing import TypeVar, Any, List, Iterable, Optional


Self = TypeVar('Self', bound='Solver')


class Solver(object):  # pragma: no cover
    def setup_solver(self):
        # type: () -> None
        raise NotImplementedError

    def set_objective(self, variables, coefficients):
        # type: (Iterable[Any], Iterable[float]) -> None
        raise NotImplementedError

    def add_variable(self, name):
        # type: (str) -> Any
        raise NotImplementedError

    def add_constraint(self, variables, coefficients, sense, rhs):
        # type: (Iterable[Any], Optional[Iterable[float]], str, float) -> None
        raise NotImplementedError

    def solve(self):
        # type: () -> List[Any]
        raise NotImplementedError

    def copy(self):
        # type: () -> Self
        raise NotImplementedError

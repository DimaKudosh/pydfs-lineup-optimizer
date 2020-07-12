from typing import TypeVar, Any, List, Iterable, Optional


Self = TypeVar('Self', bound='Solver')


class Solver:  # pragma: no cover
    def setup_solver(self) -> None:
        raise NotImplementedError

    def set_objective(self, variables: Iterable[Any], coefficients: Iterable[float]):
        raise NotImplementedError

    def add_variable(self, name: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Any:
        raise NotImplementedError

    def add_constraint(self, variables: Iterable[Any], coefficients: Optional[Iterable[float]], sign: str, rhs: float):
        raise NotImplementedError

    def solve(self) -> List[Any]:
        raise NotImplementedError

    def copy(self) -> Self:
        raise NotImplementedError

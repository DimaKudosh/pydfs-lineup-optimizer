from typing import TypeVar, Any, List, Iterable, Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from pydfs_lineup_optimizer.player import Player


Self = TypeVar('Self', bound='Solver')


class Solver:  # pragma: no cover
    def setup_solver(self) -> None:
        raise NotImplementedError

    def set_objective(self, variables: Iterable[Any], coefficients: Iterable[float]):
        raise NotImplementedError

    def add_variable(self, name: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> Any:
        raise NotImplementedError

    def add_constraint(self, variables: Iterable[Any], coefficients: Optional[Iterable[float]], sign: str, rhs: float,
                       name: Optional[str] = None):
        raise NotImplementedError

    def solve(self) -> List[Any]:
        raise NotImplementedError

    def copy(self) -> Self:
        raise NotImplementedError

    @staticmethod
    def build_player_var_name(player: 'Player', postfix: Optional[str] = None):
        parts = ['Player', player.full_name, *player.positions]
        if postfix:
            parts.append(postfix)
        return '_'.join(parts).replace(' ', '_').replace('.', '_')

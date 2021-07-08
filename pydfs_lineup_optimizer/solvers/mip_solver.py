from copy import copy
from typing import cast, Optional, List, Union, Iterable
from pydfs_lineup_optimizer.solvers.base import Solver
from pydfs_lineup_optimizer.solvers.constants import SolverSign
from pydfs_lineup_optimizer.solvers.exceptions import SolverException, SolverInfeasibleSolutionException
try:
    from mip import Model, maximize, xsum, Var
    from mip.constants import MAXIMIZE, BINARY, INTEGER, OptimizationStatus
except ImportError:
    raise ImportError('You should install mip library before using this backend')


class MIPVariable:
    def __init__(
            self,
            name: str,
            min_value: Optional[int] = None,
            max_value: Optional[int] = None,
            multiplier: Optional[int] = None
    ):
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.multiplier = multiplier
        self.__cache = None

    def setup(self, solver: Model):
        if any([self.min_value, self.max_value]):
            var = solver.add_var(name=self.name, lb=self.min_value, ub=self.max_value, var_type=INTEGER)
        else:
            var = solver.add_var(name=self.name, var_type=BINARY)
        self.__cache = var

    def get_var(self, solver: Model) -> Var:
        if self.__cache:
            var = self.__cache
        else:
            var = solver.var_by_name(self.name)
            self.__cache = var
        if self.multiplier:
            return self.multiplier * var
        return var

    def __mul__(self, other: int) -> 'MIPVariable':
        return MIPVariable(self.name, self.min_value, self.max_value, other)

    def __rmul__(self, other: int) -> 'MIPVariable':
        return self * other


class MIPConstraint:
    def __init__(
            self,
            variables: Iterable[MIPVariable],
            coefficients: Optional[Iterable[float]],
            sign: str,
            rhs: Union[float, MIPVariable],
            name: Optional[str] = None
    ):
        self.variables = variables
        self.coefficients = coefficients
        self.sign = sign
        self.rhs = rhs
        self.name = name

    def __str__(self):
        return f'{[var.name for var in self.variables]} {self.sign} {self.rhs}'

    def setup(self, solver):
        variables = self.variables
        coefficients = self.coefficients
        sign = self.sign
        rhs = self.rhs
        name = self.name
        if coefficients:
            lhs = xsum([variable.get_var(solver) * coefficient for variable, coefficient in zip(variables, coefficients)])
        else:
            lhs = xsum([var.get_var(solver) for var in variables])
        if isinstance(rhs, MIPVariable):
            rhs = rhs.get_var(solver)
        if sign == SolverSign.EQ:
            solver += (lhs == rhs, name) if name else lhs == rhs
        elif sign == SolverSign.NOT_EQ:
            solver += (lhs != rhs, name) if name else lhs != rhs
        elif sign == SolverSign.GTE:
            solver += (lhs >= rhs, name) if name else lhs >= rhs
        elif sign == SolverSign.LTE:
            solver += (lhs <= rhs, name) if name else lhs <= rhs
        else:
            raise SolverException('Incorrect constraint sign')


class MIPObjective:
    def __init__(self, variables: List[MIPVariable], coefficients: List[float]):
        self.variables = variables
        self.coefficients = coefficients

    def setup(self, solver: Model):
        solver.objective = maximize(xsum(
            variable.get_var(solver) * coefficient for variable, coefficient in zip(self.variables, self.coefficients)))


class MIPSolver(Solver):
    def __init__(self):
        self.model = None  # type: Optional[Model]
        self._vars = {}
        self._constraints = []
        self._objective = None

    def setup_solver(self) -> None:
        self.model = Model(name='pydfs_lineup_optimizer', sense=MAXIMIZE)
        self.model.solver.set_verbose(0)

    def add_variable(self, name, min_value=None, max_value=None):
        var = MIPVariable(name, min_value, max_value)
        if name in self._vars:
            raise ValueError(name)
        self._vars[name] = var
        return var

    def set_objective(self, variables, coefficients):
        self._objective = MIPObjective(variables, coefficients)

    def add_constraint(self, variables, coefficients, sign, rhs, name=None):
        self._constraints.append(MIPConstraint(
            variables,
            coefficients,
            sign,
            rhs,
            name
        ))

    def copy(self):
        new_solver = type(self)()
        new_solver.setup_solver()
        new_solver._vars = copy(self._vars)
        new_solver._constraints = copy(self._constraints)
        new_solver._objective = self._objective
        return new_solver

    def solve(self):
        model = cast(Model, self.model)
        for var in self._vars.values():
            var.setup(model)
        for constraint in self._constraints:
            constraint.setup(model)
        cast(MIPObjective, self._objective).setup(model)
        status = model.optimize()
        if status not in (OptimizationStatus.OPTIMAL, OptimizationStatus.FEASIBLE):
            raise SolverInfeasibleSolutionException([])
        result = []
        for variable in model.vars:  # type: ignore
            val = variable.x
            if val is not None and round(val) >= 1.0:
                result.append(self._vars[variable.name])
        return result

from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatusOptimal, LpBinary, LpInteger, PULP_CBC_CMD
from pydfs_lineup_optimizer.solvers.base import Solver
from pydfs_lineup_optimizer.solvers.constants import SolverSign
from pydfs_lineup_optimizer.solvers.exceptions import SolverException, SolverInfeasibleSolutionException


class PuLPSolver(Solver):
    LP_SOLVER = PULP_CBC_CMD(msg=False)

    def __init__(self):
        self.prob = LpProblem('pydfs_lineup_optimizer', LpMaximize)

    def setup_solver(self):
        pass

    def add_variable(self, name, min_value=None, max_value=None):
        name = name.replace(' ', '_')
        if any([min_value, max_value]):
            return LpVariable(name, lowBound=min_value, upBound=max_value, cat=LpInteger)
        return LpVariable(name, cat=LpBinary)

    def set_objective(self, variables, coefficients):
        self.prob += lpSum([variable * coefficient for variable, coefficient in zip(variables, coefficients)])

    def add_constraint(self, variables, coefficients, sign, rhs, name=None):
        if coefficients:
            lhs = [variable * coefficient for variable, coefficient in zip(variables, coefficients)]
        else:
            lhs = variables
        if sign == SolverSign.EQ:
            self.prob += lpSum(lhs) == rhs, name
        elif sign == SolverSign.NOT_EQ:
            self.prob += lpSum(lhs) != rhs, name
        elif sign == SolverSign.GTE:
            self.prob += lpSum(lhs) >= rhs, name
        elif sign == SolverSign.LTE:
            self.prob += lpSum(lhs) <= rhs, name
        else:
            raise SolverException('Incorrect constraint sign')

    def copy(self):
        new_solver = type(self)()
        new_solver.prob = self.prob.copy()
        return new_solver

    def solve(self):
        self.prob.solve(self.LP_SOLVER)
        if self.prob.status == LpStatusOptimal:
            result = []
            for variable in self.prob.variables():
                val = variable.value()
                if val is not None and round(val) >= 1.0:
                    result.append(variable)
            return result
        else:
            invalid_constraints = [(name or str(constraint)) for name, constraint in
                                   self.prob.constraints.items() if not constraint.valid()]
            raise SolverInfeasibleSolutionException(invalid_constraints)

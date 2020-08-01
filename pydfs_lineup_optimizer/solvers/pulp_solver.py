from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatusOptimal, LpBinary, LpInteger, PULP_CBC_CMD
from .base import Solver
from .constants import SolverSign
from .exceptions import SolverException


class PuLPSolver(Solver):
    LP_SOLVER = PULP_CBC_CMD(verbose=False, msg=False)

    def __init__(self):
        self.prob = LpProblem('Daily Fantasy Sports', LpMaximize)

    def setup_solver(self):
        pass

    def add_variable(self, name, min_value=None, max_value=None):
        if any([min_value, max_value]):
            return LpVariable(name, lowBound=min_value, upBound=max_value, cat=LpInteger)
        return LpVariable(name, cat=LpBinary)

    def set_objective(self, variables, coefficients):
        self.prob += lpSum([variable * coefficient for variable, coefficient in zip(variables, coefficients)])

    def add_constraint(self, variables, coefficients, sign, rhs):
        if coefficients:
            lhs = [variable * coefficient for variable, coefficient in zip(variables, coefficients)]
        else:
            lhs = variables
        if sign == SolverSign.EQ:
            self.prob += lpSum(lhs) == rhs
        elif sign == SolverSign.NOT_EQ:
            self.prob += lpSum(lhs) != rhs
        elif sign == SolverSign.GTE:
            self.prob += lpSum(lhs) >= rhs
        elif sign == SolverSign.LTE:
            self.prob += lpSum(lhs) <= rhs
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
            raise SolverException('Unable to solve')

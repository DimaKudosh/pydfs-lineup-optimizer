from pulp import LpProblem, LpMaximize, LpVariable, lpSum, LpStatusOptimal, LpBinary
from .base import Solver
from .constants import SolverSign
from .exceptions import SolverException


class PuLPSolver(Solver):
    LP_SOLVER = None

    def __init__(self):
        self.prob = None

    def setup_solver(self):
        self.prob = LpProblem('Daily Fantasy Sports', LpMaximize)

    def add_variable(self, name):
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
                if variable.value() == 1.0:
                    result.append(variable)
            return result
        else:
            raise SolverException('Unable to solve')

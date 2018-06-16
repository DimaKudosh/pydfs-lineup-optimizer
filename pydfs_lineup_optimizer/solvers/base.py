class Solver(object):  # pragma: no cover
    def setup_solver(self):
        raise NotImplementedError

    def set_objective(self, variables, coefficients):
        raise NotImplementedError

    def add_variable(self, name, low_bound, up_bound):
        raise NotImplementedError

    def add_constraint(self, variables, coefficients, sense, rhs):
        raise NotImplementedError

    def solve(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

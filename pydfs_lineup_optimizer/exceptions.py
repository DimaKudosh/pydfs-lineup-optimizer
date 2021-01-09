from typing import List


class LineupOptimizerException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class LineupOptimizerIncorrectTeamName(LineupOptimizerException):
    pass


class LineupOptimizerIncorrectPositionName(LineupOptimizerException):
    pass


class LineupOptimizerIncorrectCSV(LineupOptimizerException):
    def __init__(self, message: str = 'Incorrect csv format!'):
        super(LineupOptimizerIncorrectCSV, self).__init__(message)


class GenerateLineupException(LineupOptimizerException):
    def __init__(self, invalid_constraints: List[str]):
        self.invalid_constraints = invalid_constraints

    def __str__(self):
        msg = 'Can\'t generate lineups.'
        if self.invalid_constraints:
            msg += ' Following constraints are not valid: %s' % ','.join(self.invalid_constraints)
        return msg

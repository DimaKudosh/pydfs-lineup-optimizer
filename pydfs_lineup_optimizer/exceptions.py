class LineupOptimizerException(Exception):
    def __init__(self, message):
        # type: (str) -> None
        self.message = message

    def __str__(self):
        return self.message


class LineupOptimizerIncorrectTeamName(LineupOptimizerException):
    pass


class LineupOptimizerIncorrectPositionName(LineupOptimizerException):
    pass


class LineupOptimizerIncorrectCSV(LineupOptimizerException):
    def __init__(self, message='Incorrect csv format!'):
        # type: (str) -> None
        super(LineupOptimizerIncorrectCSV, self).__init__(message)

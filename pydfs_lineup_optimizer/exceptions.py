class LineupOptimizerException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class LineupOptimizerIncorrectTeamName(LineupOptimizerException):
    pass


class LineupOptimizerIncorrectPositionName(LineupOptimizerException):
    pass

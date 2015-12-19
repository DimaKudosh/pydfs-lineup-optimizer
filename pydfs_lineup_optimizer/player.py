class Player:
    def __init__(self, first_name, last_name, position, team, opponent, salary, fppg, is_injured=False):
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.team = team
        self.opponent = opponent
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured

    def __str__(self):
        return "{}{}{}{}{}".format(
            "{:<30}".format(self.full_name),
            "{:<4}".format(self.position),
            "{:<5}".format(self.team),
            "{:<6}".format(str(self.fppg)),
            "{:<10}".format(str(self.salary) + '$')
        )

    @property
    def full_name(self):
        return self.first_name + self.last_name

    @property
    def efficiency(self):
        return self.fppg / self.salary

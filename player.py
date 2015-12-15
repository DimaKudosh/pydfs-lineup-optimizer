class Player:
    def __init__(self, first_name, last_name, position, team, salary, fppg, is_injured=False):
        self.first_name = first_name
        self.last_name = last_name
        self.position = position
        self.team = team
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured

    def __str__(self):
        return "{} {}  {} {}  {}-{}$".format(self.first_name, self.last_name, self.position, self.team, self.fppg, self.salary)

    @property
    def efficiency(self):
        return self.fppg / self.salary

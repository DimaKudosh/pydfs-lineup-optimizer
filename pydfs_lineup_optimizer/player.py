class Player(object):
    def __init__(self, id,  first_name, last_name, positions, team, salary, fppg, is_injured=False):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.positions = positions
        self.team = team
        self.salary = salary
        self.fppg = fppg
        self.is_injured = is_injured

    def __str__(self):
        return "{}{}{}{}{}".format(
            "{:<30}".format(self.full_name),
            "{:<4}".format(self.positions),
            "{:<15}".format(self.team),
            "{:<6}".format(str(self.fppg)),
            "{:<10}".format(str(self.salary) + '$')
        )

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def efficiency(self):
        return round(self.fppg / self.salary, 2)

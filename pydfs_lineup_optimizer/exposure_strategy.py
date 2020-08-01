from collections import defaultdict
from typing import Dict, List


class BaseExposureStrategy:
    def __init__(self, exposures: Dict[str, float], total_lineups: int) -> None:
        self.exposures = exposures
        self.total_lineups = total_lineups
        self.used_vars = defaultdict(int)  # type: Dict[str, int]

    def set_used(self, variables: List[str]):
        for var in variables:
            if var in self.exposures:
                self.used_vars[var] += 1

    def is_reached_exposure(self, var: str) -> bool:
        raise NotImplementedError


class TotalExposureStrategy(BaseExposureStrategy):
    def is_reached_exposure(self, var):
        max_exposure = self.exposures.get(var)
        if not max_exposure:
            return False
        used = self.used_vars.get(var, 0)
        return max_exposure <= used / self.total_lineups


class AfterEachExposureStrategy(BaseExposureStrategy):
    def __init__(self, exposures, total_lineups):
        super().__init__(exposures, total_lineups)
        self.current_iteration = 0

    def set_used(self, variables: List[str]):
        super().set_used(variables)
        self.current_iteration += 1

    def is_reached_exposure(self, var):
        max_exposure = self.exposures.get(var)
        if not max_exposure or not self.current_iteration:
            return False
        used = self.used_vars.get(var, 0)
        return max_exposure <= used / self.current_iteration

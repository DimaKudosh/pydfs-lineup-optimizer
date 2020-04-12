from collections import defaultdict
from typing import Type, DefaultDict, Dict
from pydfs_lineup_optimizer.settings import BaseSettings


class SitesRegistry:
    SETTINGS_MAPPING = defaultdict(dict)  # type: DefaultDict[str, Dict[str, Type[BaseSettings]]]

    @classmethod
    def register_settings(cls, settings_cls: Type[BaseSettings]) -> Type[BaseSettings]:
        cls.SETTINGS_MAPPING[settings_cls.site][settings_cls.sport] = settings_cls
        return settings_cls

    @classmethod
    def get_settings(cls, site: str, sport: str) -> Type[BaseSettings]:
        try:
            return cls.SETTINGS_MAPPING[site][sport]
        except KeyError:
            raise NotImplementedError

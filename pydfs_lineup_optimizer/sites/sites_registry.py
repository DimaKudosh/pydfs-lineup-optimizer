from collections import defaultdict
from typing import Type, DefaultDict, Dict
from pydfs_lineup_optimizer.settings import BaseSettings
from pydfs_lineup_optimizer.lineup_importer import CSVImporter


class SitesRegistry:
    SETTINGS_MAPPING = defaultdict(dict)  # type: DefaultDict[str, Dict[str, Type[BaseSettings]]]
    CSV_IMPORTERS_MAPPING = {}  # type: Dict[str, Type[CSVImporter]]

    @classmethod
    def register_settings(cls, settings_cls: Type[BaseSettings]) -> Type[BaseSettings]:
        cls.SETTINGS_MAPPING[settings_cls.site][settings_cls.sport] = settings_cls
        return settings_cls

    @classmethod
    def register_csv_importer(cls, importer_cls: Type[CSVImporter]) -> Type[CSVImporter]:
        cls.CSV_IMPORTERS_MAPPING[importer_cls.site] = importer_cls
        return importer_cls

    @classmethod
    def get_settings(cls, site: str, sport: str) -> Type[BaseSettings]:
        try:
            return cls.SETTINGS_MAPPING[site][sport]
        except KeyError:
            raise NotImplementedError

    @classmethod
    def get_csv_importer(cls, site: str) -> Type[CSVImporter]:
        try:
            return cls.CSV_IMPORTERS_MAPPING[site]
        except KeyError:
            raise NotImplementedError

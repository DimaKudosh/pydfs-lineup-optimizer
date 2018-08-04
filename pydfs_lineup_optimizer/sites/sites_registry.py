from collections import defaultdict
from typing import Type, Tuple
from pydfs_lineup_optimizer.settings import BaseSettings
from pydfs_lineup_optimizer.lineup_importer import CSVImporter


class SitesRegistry(object):
    SETTINGS_MAPPING = defaultdict(dict)
    CSV_IMPORTERS_MAPPING = {}

    @classmethod
    def register_settings(cls, settings_cls):
        # type: (Type[BaseSettings]) -> Type[BaseSettings]
        cls.SETTINGS_MAPPING[settings_cls.site][settings_cls.sport] = settings_cls
        return settings_cls

    @classmethod
    def register_csv_importer(cls, importer_cls):
        # type: (Type[CSVImporter]) -> Type[CSVImporter]
        cls.CSV_IMPORTERS_MAPPING[importer_cls.site] = importer_cls
        return importer_cls

    @classmethod
    def get_optimizer_args(cls, site, sport):
        # type: (str, str) -> Tuple[BaseSettings, CSVImporter]
        try:
            return cls.SETTINGS_MAPPING[site][sport], cls.CSV_IMPORTERS_MAPPING[site]
        except KeyError:
            raise NotImplementedError

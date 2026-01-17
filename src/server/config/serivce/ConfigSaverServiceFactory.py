from src.server.config.repository.ConfigRepositoryFactory import ConfigRepositoryFactory
from src.server.config.serivce.ConfigSaverServiceImpl import ConfigSaverServiceImpl
from src.server.config.serivce.ConfigSavingService import ConfigSavingService


class ConfigSaverServiceFactory:
    _instance = None

    @classmethod
    def get_config_saver(cls) -> ConfigSavingService:
        if cls._instance is None:
            config_repo = ConfigRepositoryFactory.get_config_repository()
            cls._instance = ConfigSaverServiceImpl(config_repo)

        return cls._instance
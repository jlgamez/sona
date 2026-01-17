from src.server.config.repository.config_repository import ConfigRepository, ConfigRepositoryImpl


class ConfigRepositoryFactory:
    _instance: ConfigRepository = None

    @classmethod
    def get_config_repository(cls) -> ConfigRepository:
        if cls._instance is None:
            cls._instance = ConfigRepositoryImpl()
        return cls._instance
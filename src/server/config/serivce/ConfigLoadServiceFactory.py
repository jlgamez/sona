from src.server.config.repository.ConfigRepositoryFactory import ConfigRepositoryFactory
from src.server.config.repository.config_repository import ConfigRepositoryImpl
from src.server.config.serivce.config_load_service import ConfigLoadService
from src.server.config.serivce.config_load_service_impl import ConfigLoadServiceImpl
from src.server.hot_key.service.HotKeyServiceFactory import HotKeyServiceFactory
from src.server.models.service.LocalModelServiceFactory import LocalModelServiceFactory


class ConfigLoadServiceFactory:
    _instance: ConfigLoadService = None

    @classmethod
    def get_config_loader(cls) -> ConfigLoadService:
        if cls._instance is None:
            config_repo = ConfigRepositoryFactory.get_config_repository()
            hot_key_service = HotKeyServiceFactory.get_hot_key_service()
            model_service = LocalModelServiceFactory.get_local_model_service()
            config_defaults = {
                "hot_key": hot_key_service.get_default_hot_key().name,
                "model": model_service.get_default_model_name(),
            }

            cls._instance = ConfigLoadServiceImpl(config_repo, config_defaults)
        return cls._instance

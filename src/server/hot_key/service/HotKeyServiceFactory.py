from src.server.hot_key.repository.HotKeyRepositoryFactory import HotKeyRepositoryFactory
from src.server.hot_key.service.HotKeyService import HotKeyService, HotKeyServiceImpl


class HotKeyServiceFactory:
    _instance: HotKeyService = None

    @classmethod
    def get_hot_key_service(cls) -> HotKeyService:
        if cls._instance is None:
            cls._instance = HotKeyServiceImpl(HotKeyRepositoryFactory.get_hot_key_repository())
        return cls._instance

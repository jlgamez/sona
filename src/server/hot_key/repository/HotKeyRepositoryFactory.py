from src.server.hot_key.repository.hot_key_repository import HotKeyRepository, HotKeyRepositoryImpl


class HotKeyRepositoryFactory:
    _instance = None

    @classmethod
    def get_hot_key_repository(cls) -> HotKeyRepository:
        if cls._instance is None:
            cls._instance = HotKeyRepositoryImpl()
        return cls._instance
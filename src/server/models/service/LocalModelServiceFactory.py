from src.server.models.repository.ModelRepositoryFactory import ModelRepositoryFactory
from src.server.models.service.LocalModelService import LocalModelService, LocalModelServiceImpl


class LocalModelServiceFactory:
    _instance: LocalModelService = None

    @classmethod
    def get_local_model_service(cls) -> LocalModelService:
        if cls._instance is None:
            cls._instance = LocalModelServiceImpl(ModelRepositoryFactory.get_model_repository())
        return cls._instance
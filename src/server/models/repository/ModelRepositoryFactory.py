from src.server.models.repository.ModelRepository import ModelRepository, ModelRepositoryImpl


class ModelRepositoryFactory:
    _instance: ModelRepository = None

    @classmethod
    def get_model_repository(cls) -> ModelRepository:
        if cls._instance is None:
            cls._instance = ModelRepositoryImpl()
        return cls._instance
from typing import Protocol, List

from src.server.exception.model_in_system_exception import ModelInSystemException
from src.server.models.entity.transcription_model_info import TranscriptionModelInfo
from src.server.models.repository.model_repository import ModelRepository


class LocalModelService(Protocol):

    def get_available_models(self) -> List[TranscriptionModelInfo]:
        pass

    def is_model_in_system(self, model_name: str) -> bool:
        pass

    def get_default_model_name(self) -> str:
        pass

    def download_model(self, model_name: str) -> None:
        pass


class LocalModelServiceImpl(LocalModelService):

    def __init__(self, model_repository: ModelRepository):
        self._model_repository = model_repository

    def get_available_models(self) -> List[TranscriptionModelInfo]:
        return [
            TranscriptionModelInfo(
                name=name,
                english_only=info[1],
                required_ram=info[2],
                relative_speed=info[3],
                in_system=self.is_model_in_system(name),
            )
            for name, info in self._model_repository.read_available_models().items()
        ]

    def is_model_in_system(self, model_name: str) -> bool:
        return self._model_repository.is_model_in_system(model_name)

    def get_default_model_name(self) -> str:
        return self._model_repository.get_default_model_info()[0]

    def download_model(self, model_name: str) -> None:
        available_models = self._model_repository.read_available_models()
        if model_name not in available_models:
            raise ValueError(f"Model '{model_name}' is not recognized as available.")

        if self.is_model_in_system(model_name):
            raise ModelInSystemException(
                f"Model '{model_name}' is already in the system."
            )

        from src.core.transcription.download_model import download_model_async

        download_model_async(model_name)

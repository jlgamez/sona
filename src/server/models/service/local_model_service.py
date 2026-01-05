from typing import Protocol, List

from src.server.models.entity.transcription_model_info import TranscriptionModelInfo
from src.server.models.repository.model_repository import ModelRepository


class LocalModelService(Protocol):

    def get_available_models(self) -> List[TranscriptionModelInfo]:
        pass

    def is_model_in_system(self, model_name: str) -> bool:
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

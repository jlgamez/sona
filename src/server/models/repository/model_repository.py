from typing import Protocol, Tuple

from src.server.models.repository.model_constants import (
    MODELS_INFO,
    WHISPER_CACHE_DIR,
    DEFAULT_MODEL,
)


class ModelRepository(Protocol):

    def read_available_models(self) -> dict:
        pass

    def is_model_in_system(self, model_name: str) -> bool:
        pass

    def get_default_model_info(self) -> Tuple[str, Tuple[str, bool, str, str]]:
        pass


class ModelRepositoryImpl(ModelRepository):

    def read_available_models(self) -> dict:
        return MODELS_INFO

    def is_model_in_system(self, model_name: str) -> bool:
        "Check if a model is present in the local Whisper cache."
        model_info = MODELS_INFO.get(model_name)
        if model_info is None:
            return False
        whisper_cache_filename = model_info[0]  # First element is the filename
        return (WHISPER_CACHE_DIR / whisper_cache_filename).is_file()

    def get_default_model_info(self) -> Tuple[str, Tuple[str, bool, str, str]]:
        return DEFAULT_MODEL

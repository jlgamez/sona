from pathlib import Path
from typing import Final

from src.server.model.model_constants import MODEL_INFO


# Whisper cache directory on disk
WHISPER_CACHE_DIR: Final[Path] = Path.home() / ".cache" / "whisper"


def is_model_in_system(model_name: str) -> bool:
    "Check if a model is present in the local Whisper cache."

    model_info = MODEL_INFO.get(model_name)
    if model_info is None:
        return False
    whisper_cache_filename = model_info[0]  # First element is the filename
    return (WHISPER_CACHE_DIR / whisper_cache_filename).is_file()

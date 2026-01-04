from typing import List

from src.server.config.entity.user_config import TranscriptionModelInfo
from src.server.model.local_model_service import is_model_in_system
from src.server.model.model_constants import MODEL_INFO


def available_models() -> List[TranscriptionModelInfo]:
    """Return a list of all available transcription models."""
    return [
        TranscriptionModelInfo(
            name=name,
            english_only=info[1],
            required_ram=info[2],
            relative_speed=info[3],
            in_system=is_model_in_system(name),
        )
        for name, info in MODEL_INFO.items()
    ]

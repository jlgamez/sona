"""AITranscriber gateway for decoupling core logic from Whisper imports."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import (
    Any,
    Dict,
    Optional,
    Protocol,
    runtime_checkable,
    TYPE_CHECKING,
)
from .device.device_manager import DeviceManager

if TYPE_CHECKING:  # pragma: no cover
    import whisper  # type: ignore


@runtime_checkable
class AITranscriber(Protocol):
    """Minimal transcription gateway API."""

    def load(self) -> None: ...

    def transcribe(self, audio: Path) -> Dict[str, Any]: ...

    def teardown(self) -> None: ...


class AITranscriberImpl(AITranscriber):
    """Thread-safe Whisper adapter with lazy imports and device auto-detection."""

    _model: Optional[Any] = None
    _model_lock = threading.Lock()

    def __init__(
        self,
        model_name: str,
        device_manager: Optional[DeviceManager] = None,
    ) -> None:
        self._model_name = model_name
        self._device_manager = device_manager or DeviceManager()
        self._device = self._device_manager.get_platform_device()

    def load(self) -> None:
        with self._model_lock:
            if AITranscriberImpl._model is not None:
                return
            whisper_module = self._lazy_import_whisper()
            AITranscriberImpl._model = whisper_module.load_model(
                self._model_name, device=self._device
            )

    def transcribe(self, audio: Path) -> Dict[str, Any]:
        if AITranscriberImpl._model is None:
            self.load()
        model = AITranscriberImpl._model
        if model is None:
            raise RuntimeError("Whisper model failed to load")

        try:
            return model.transcribe(audio=str(audio))
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Transcription failed") from exc

    def teardown(self) -> None:
        with self._model_lock:
            if AITranscriberImpl._model is None:
                return
            self._device_manager.clear_device_cache()
            AITranscriberImpl._model = None

    @staticmethod
    def _lazy_import_whisper() -> Any:
        try:
            import whisper  # type: ignore

            return whisper
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Failed to import whisper") from exc

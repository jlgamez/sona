from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Protocol, runtime_checkable
import threading
import whisper

from .device_selector import DeviceSelector, DeviceSelectorImpl

@runtime_checkable
class ModelAdapter(Protocol):
    """ModelAdapter

    Responsibility:
        Abstracts the interface for any AI model capable of transcribing audio, decoupling the application from a specific implementation (e.g., Whisper).
        Allows for easy swapping or mocking of the underlying model for testing or future extensibility.

    Interface:
        * transcribe(audio: Any, **kwargs) -> dict
            Transcribes the given audio input and returns a dictionary containing the transcription and metadata.
    """

    def transcribe(self, audio: Path) -> dict:
        """Transcribe the given audio input and return a dictionary with the transcription and metadata."""
        pass


class ModelAdapterImpl(ModelAdapter):
    """ModelAdapterImpl

    Responsibility:
        Implements the ModelAdapter protocol using OpenAI Whisper.
        Loads the Whisper model as a singleton on initialization, with thread-safe access.
        Uses DeviceSelector for hardware detection and optimization.

    Interface:
        * transcribe(audio: Path) -> dict
            Transcribes the given audio file and returns a dictionary with transcription and metadata.
    """

    _model: Optional[whisper.Whisper] = None
    _model_lock = threading.Lock()
    _device: Optional[str] = None

    MODEL_NAME = "base"

    def __init__(self, device_selector: Optional[DeviceSelector] = None):
        """Initialize the ModelAdapterImpl and load the Whisper model as a singleton.

        Args:
            device_selector: Optional DeviceSelector for hardware detection. Defaults to DeviceSelectorImpl.
        """
        self._device_selector = device_selector or DeviceSelectorImpl()
        ModelAdapterImpl._device = self._device_selector.select_device()
        self._load_model()

    def _load_model(self) -> whisper.Whisper:
        """Load the Whisper model as a singleton in a thread-safe manner.

        Returns:
            The loaded Whisper model instance.
        """
        with self._model_lock:
            if ModelAdapterImpl._model is None:
                ModelAdapterImpl._model = whisper.load_model(self.MODEL_NAME, device=ModelAdapterImpl._device)
            return ModelAdapterImpl._model

    def transcribe(self, audio: Path) -> Dict[str, Any]:
        """Transcribe the given audio file using Whisper and return transcription and metadata.

        Args:
            audio: Path to the audio file to transcribe.

        Returns:
            Dictionary containing transcription text and metadata from Whisper.
        """
        # Whisper API accepts either a numpy.ndarray waveform or a string path. Cast Path -> str for compatibility.
        return ModelAdapterImpl._model.transcribe(audio=str(audio))

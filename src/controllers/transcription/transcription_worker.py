from __future__ import annotations

from typing import Any, Protocol, runtime_checkable, Union
from pathlib import Path

AudioInput = Union[Path, bytes, memoryview]


@runtime_checkable
class TranscriptionWorker(Protocol):
    """TranscriptionWorker

    Responsibility:
        Execute Whisper inference using the provided audio input, model, device,
        and fp16 flag. Does not own IO or cleanup.

    Interface:
        * transcribe(audio, model, device, fp16, language) -> str
    """

    def transcribe(
        self,
        audio: AudioInput,
        model: Any,
        device: str,
        fp16: bool,
        language: str | None = None,
    ) -> str:
        """Return transcribed text for the provided audio input."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class WhisperModelProvider(Protocol):
    """WhisperModelProvider

    Responsibility:
        Lazy-load and cache the Whisper model on first use for the chosen device.
        Expose a singleton-style getter to avoid repeated cold starts.

    Interface:
        * get_model(device: str) -> Any
    """

    def get_model(self, device: str) -> Any:
        """Return a cached Whisper model, loading it lazily for the device."""

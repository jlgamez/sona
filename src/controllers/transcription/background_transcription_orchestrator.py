from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class BackgroundTranscriptionOrchestrator(Protocol):
    """BackgroundTranscriptionOrchestrator

    Responsibility:
        Coordinate background transcription off the hotkey thread. Internally
        compose DeviceSelector, WhisperModelProvider, AudioLoader,
        TranscriptionWorker, CleanupService, and TranscriptionResultHandler.
        Ensure cleanup on success and error.

    Interface:
        * submit(path: Path) -> None
        * shutdown() -> None
    """

    def submit(self, path: Path) -> None:
        """Enqueue transcription for the given audio file path."""

    def shutdown(self) -> None:
        """Tear down worker resources (threads/processes) at application exit."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable, Union

AudioInput = Union[Path, bytes, memoryview]


@runtime_checkable
class CleanupService(Protocol):
    """CleanupService

    Responsibility:
        Best-effort cleanup for temporary files and in-memory or mapped audio
        resources. Must be idempotent and resilient to IO errors.

    Interface:
        * delete_file(path: Path) -> None
        * release_audio(audio: AudioInput) -> None
    """

    def delete_file(self, path: Path) -> None:
        """Remove the temp audio file if it exists (idempotent)."""

    def release_audio(self, audio: AudioInput) -> None:
        """Release in-memory or mapped audio resources (idempotent)."""

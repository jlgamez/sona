from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable, Union

AudioInput = Union[Path, bytes, memoryview]


@runtime_checkable
class AudioLoader(Protocol):
    """AudioLoader

    Responsibility:
        Validate the temp audio file and provide an efficient input handle:
        path streaming for large clips or in-memory buffer for small clips.
        Own releasing related resources (e.g., closing mmap).

    Interface:
        * load(path: Path) -> AudioInput
        * release(audio: AudioInput) -> None
    """

    def load(self, path: Path) -> AudioInput:
        """Return a validated audio input (path or in-memory data)."""

    def release(self, audio: AudioInput) -> None:
        """Free resources associated with the audio input."""



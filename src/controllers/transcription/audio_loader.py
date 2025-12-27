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


class SimpleAudioLoader:
    """SimpleAudioLoader

    Responsibility:
        Concrete implementation that validates audio files and provides
        efficient input handles. Uses in-memory loading for small files
        (< 1MB) and path streaming for larger files.

    Interface:
        * load(path: Path) -> AudioInput
        * release(audio: AudioInput) -> None
    """

    # Threshold: files smaller than this are loaded into memory
    MEMORY_THRESHOLD_BYTES: int = 1_048_576  # 1 MB

    def load(self, path: Path) -> AudioInput:
        """Return a validated audio input (path or in-memory data).
        Args:
            path: Path to the audio file
        Returns:
            AudioInput: Either a Path (for large files) or bytes (for small files)
        Raises:
            FileNotFoundError: If the audio file does not exist
            OSError: If the file cannot be read
        """
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        if not path.is_file():
            raise OSError(f"Path is not a file: {path}")

        file_size = path.stat().st_size

        # For small files, load into memory to avoid disk I/O overhead
        if file_size < self.MEMORY_THRESHOLD_BYTES:
            with open(path, 'rb') as f:
                return f.read()

        # For larger files, return the path and let Whisper stream from disk
        return path

    def release(self, audio: AudioInput) -> None:
        """Free resources associated with the audio input.
        Args:
            audio: The audio input to release (Path or bytes)
        Note:
            For simple implementation, bytes are garbage collected automatically.
            Path objects require no explicit cleanup. This method is provided
            for protocol compliance and future extensibility (e.g., mmap support).
        """
        # For bytes and Path, Python's GC handles cleanup
        # This is a no-op but keeps the interface consistent
        pass

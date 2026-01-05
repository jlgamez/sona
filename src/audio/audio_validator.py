from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class AudioValidator(Protocol):
    """AudioValidator

    Responsibility:
        Validate that an audio file exists, is readable, and meets basic requirements
        before passing it to the transcription pipeline. Pure validation only—no
        loading or buffering.

    Interface:
        * validate(path: Path) -> bool
    """

    def validate(self, path: Path) -> bool:
        """Validate the audio file.

        Args:
            path: Path to the audio file

        Returns:
            True if valid

        Raises:
            FileNotFoundError: If the audio file does not exist
            OSError: If the file cannot be read or is invalid
        """


class AudioValidatorImpl(AudioValidator):
    """AudioValidatorImpl

    Responsibility:
        Concrete implementation that validates audio files for existence,
        readability, and basic format requirements. Strictly IO-bound validation
        without loading content into memory.

    Interface:
        * validate(path: Path) -> bool
    """

    def validate(self, path: Path) -> bool:
        """Validate the audio file exists and is readable.

        Args:
            path: Path to the audio file

        Returns:
            True if valid

        Raises:
            FileNotFoundError: If the audio file does not exist
            OSError: If the file cannot be read or is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        if not path.is_file():
            raise OSError(f"Path is not a file: {path}")

        # Check if file is readable
        if not path.stat().st_size > 0:
            raise OSError(f"Audio file is empty: {path}")

        return True

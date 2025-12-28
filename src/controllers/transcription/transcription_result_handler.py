from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class TranscriptionResultHandler(Protocol):
    """TranscriptionResultHandler

    Responsibility:
        Route transcription results or errors to the app layer (e.g., clipboard,
        event bus). Keeps output concerns decoupled from inference.

    Interface:
        * handle_success(text: str) -> None
        * handle_error(exc: Exception) -> None
    """

    def handle_success(self, text: str) -> None:
        """Deliver a successful transcription result."""

    def handle_error(self, exc: Exception) -> None:
        """Report a failure with context."""


class TranscriptionResultHandlerImpl(TranscriptionResultHandler):
    def handle_success(self, text: str) -> None:
        print(f"[TRANSCRIPTION SUCCESS] {text}")

    def handle_error(self, exc: Exception) -> None:
        print(f"[TRANSCRIPTION ERROR] {type(exc).__name__}: {exc}")


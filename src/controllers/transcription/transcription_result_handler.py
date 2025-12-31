from __future__ import annotations

import subprocess
from typing import Protocol, runtime_checkable
from pynput.keyboard import Key, Controller as KeyboardController


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
        # add new line
        text_with_newline = text + "\n\n"
        # TODO: adapt copy paste cmd for cross platform
        try:
            copy = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            if copy is None:
                raise RuntimeError("Failed to launch pbcopy")
            copy.stdin.write(text_with_newline.encode("utf-8"))
            copy.stdin.close()
            copy.wait(timeout=2)
        except Exception as exception:
            self.handle_error(exception)
            return

        try:
            self._paste_action()
        except Exception as exception:
            self.handle_error(exception)

    def _paste_action(self):
        if KeyboardController is None or Key is None:
            raise RuntimeError("Failed to find pynput")

        keyboard = KeyboardController()
        keyboard.press(Key.cmd)
        keyboard.press("v")
        keyboard.release(Key.cmd)
        keyboard.release("v")



    def handle_error(self, exc: Exception) -> None:
        print(f"[TRANSCRIPTION ERROR] {type(exc).__name__}: {exc}")


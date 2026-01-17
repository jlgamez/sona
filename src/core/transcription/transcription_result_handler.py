from __future__ import annotations

from typing import Protocol, runtime_checkable
from pynput.keyboard import Key, Controller as KeyboardController

from src.server.config.serivce.ConfigLoadServiceFactory import ConfigLoadServiceFactory
from src.utils import clipboard


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

        try:
            clipboard.set_text(text_with_newline)
        except Exception as exception:
            self.handle_error(exception)
            return

        try:
            config = ConfigLoadServiceFactory.get_config_loader().load_config()
            clipboard_behaviour = config.clipboard_behaviour

            if clipboard_behaviour.autonomous_pasting:
                self._paste_action()

            should_keep_output_in_clipboard = (
                clipboard_behaviour.keep_output_in_clipboard
            )
            if not should_keep_output_in_clipboard:
                # Wipe clipboard contents after we've pasted (or immediately if paste is disabled)
                clipboard.clear()

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

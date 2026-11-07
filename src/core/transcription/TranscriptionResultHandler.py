from __future__ import annotations

import threading
import time
from typing import Protocol, runtime_checkable
from pynput.keyboard import Key, Controller as KeyboardController

from src.server.config.serivce.ConfigLoadServiceFactory import ConfigLoadServiceFactory
from src.utils import clipboard

# Time for the clipboard write to be visible before sending Cmd+V.
PASTE_DELAY_SECONDS = 0.1
# Time for the target app to read the clipboard before the previous contents are restored.
RESTORE_DELAY_SECONDS = 0.5

# Serializes the set / paste / restore sequence so overlapping results cannot
# capture each other's text as the "previous" clipboard.
_clipboard_lock = threading.Lock()


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

        with _clipboard_lock:
            try:
                clipboard.set_text(text_with_newline)
            except Exception as exception:
                self.handle_error(exception)
                return

            try:
                config = ConfigLoadServiceFactory.get_config_loader().load_config()
                clipboard_behaviour = config.clipboard_behaviour

                pasted = False
                if clipboard_behaviour.autonomous_pasting:
                    time.sleep(PASTE_DELAY_SECONDS)
                    self._paste_action()
                    pasted = True

                should_keep_output_in_clipboard = (
                    clipboard_behaviour.keep_output_in_clipboard
                )
                # Without a paste the clipboard is the only output, so it is kept
                # regardless of keep_output_in_clipboard.
                if pasted and not should_keep_output_in_clipboard:
                    # Let the target app read the clipboard before restoring it.
                    time.sleep(RESTORE_DELAY_SECONDS)
                    clipboard.clear()

            except Exception as exception:
                self.handle_error(exception)

    def _paste_action(self):
        if KeyboardController is None or Key is None:
            raise RuntimeError("Failed to find pynput")

        keyboard = KeyboardController()
        # Cmd is released after "v" and even if the tap fails.
        with keyboard.pressed(Key.cmd):
            keyboard.tap("v")

    def handle_error(self, exc: Exception) -> None:
        print(f"[TRANSCRIPTION ERROR] {type(exc).__name__}: {exc}")

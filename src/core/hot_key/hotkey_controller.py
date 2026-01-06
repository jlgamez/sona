from __future__ import annotations

from typing import Protocol


class HotkeyController(Protocol):
    """HotkeyController

    Responsibility:
        Defines the contract for setting up a global hotkey listener in a non-blocking manner.
        Implementations are responsible for initializing and starting the hotkey listener,
        ensuring it runs on a background thread and handles OS-level permissions gracefully.

    Interface:
        * setup_key_listener(): Initializes and starts the hotkey listener, specifying the hotkey
          combination and ensuring non-blocking operation. Should handle macOS accessibility errors
          by surfacing clear exceptions or log messages instead of crashing.
    """

    def start_listening(self) -> None:
        """Set up the global hotkey listener.

        This method is responsible for initializing and starting the hotkey
        listener in a non-blocking manner. It should handle any necessary
        configuration, such as specifying the hotkey combination and ensuring
        that the listener runs on a background thread.
        """

    def stop_listening(self) -> None:
        """Stop the global hotkey listener if it is currently running."""

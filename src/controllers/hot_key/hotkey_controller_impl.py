from __future__ import annotations

from typing import Callable, Optional

from pynput import keyboard
from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode

from .hotkey_actions import HotKeyActions
from .hotkey_controller import HotkeyController


class HotKeyControllerImpl(HotkeyController):
    """PynputHotkeyController

    Responsibility:
        Concrete implementation of :class:`HotkeyController` that uses the
        ``pynput`` library to listen for a specific global hotkey and invoke
        user-provided callbacks on press and release.

    Interface:
        Initialize the controller with two callables, ``on_press_callback``
        and ``on_release_callback``, which are invoked when the configured
        hotkey is pressed and released, respectively.

        The actual registration of the global hotkey and the background
        listener loop is managed internally. The public methods
        :meth:`on_press` and :meth:`on_release` simply delegate to the
        configured callbacks and satisfy the :class:`HotkeyController`
        protocol.
    """

    HOTKEY = keyboard.Key.ctrl_l

    def __init__(
        self,
        hot_key_actions: HotKeyActions,
    ) -> None:
        # Import locally to avoid hard dependency at module import time and to
        # allow this module to be imported in environments where ``pynput`` is
        # not available (e.g., some CI setups). Any ImportError will surface
        # when constructing the controller, which callers can handle.
        from pynput import keyboard  # type: ignore

        self._keyboard = keyboard
        self._hot_key : HotKeyActions = hot_key_actions
        self._listener: Optional[KeyboardListener] = None

    def start_listening(self) -> None:
        if self._listener is not None:
            return
        self._listener = self._keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def _on_press(self, key: Key | KeyCode) -> None:
        if key == self.HOTKEY:
            self._hot_key.on_press()

    def _on_release(self, key: Key | KeyCode) -> None:
        if key == self.HOTKEY:
            self._hot_key.on_release()

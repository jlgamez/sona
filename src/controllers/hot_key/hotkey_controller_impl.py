from __future__ import annotations

from typing import Optional, Any, Set

from pynput.keyboard import Listener as KeyboardListener, Key, KeyCode

from .hotkey_actions import HotKeyActions
from .hotkey_controller import HotkeyController
from .hotkey_mapping import HotkeyDefinition, map_hotkey_string


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

    def __init__(
        self,
        hot_key_actions: HotKeyActions,
        hotkey_str: str = "ctrl_l",
    ) -> None:
        # Import locally to avoid hard dependency at module import time and to
        # allow this module to be imported in environments where ``pynput`` is
        # not available (e.g., some CI setups). Any ImportError will surface
        # when constructing the controller, which callers can handle.
        from pynput import keyboard as _keyboard  # type: ignore

        self._keyboard = _keyboard
        self._hot_key: HotKeyActions = hot_key_actions
        self._listener: Optional[KeyboardListener] = None

        # Map configured hotkey string to an internal definition. This keeps
        # the controller decoupled from how we persist config.
        self._hotkey_def: HotkeyDefinition = map_hotkey_string(
            hotkey_str=hotkey_str, keyboard_module=self._keyboard
        )
        # Track currently pressed keys so we can support chords.
        self._pressed_keys: Set[Any] = set()

    def start_listening(self) -> None:
        if self._listener is not None:
            return
        self._listener = self._keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def _on_press(self, key: Key | KeyCode) -> None:
        # Record key as pressed
        self._pressed_keys.add(key)

        if self._hotkey_def.type == "single":
            # Single-key hotkey: trigger when this key is pressed.
            if key in self._hotkey_def.keys:
                self._hot_key.on_press()
        else:
            # Chord hotkey: trigger when all required keys are currently held.
            if self._hotkey_def.keys.issubset(self._pressed_keys):
                self._hot_key.on_press()

    def _on_release(self, key: Key | KeyCode) -> None:
        # Mark key as released
        if key in self._pressed_keys:
            self._pressed_keys.remove(key)

        if key in self._hotkey_def.keys:
            self._hot_key.on_release()

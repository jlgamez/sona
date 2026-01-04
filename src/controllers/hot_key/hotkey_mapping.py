from __future__ import annotations

"""Helpers for mapping configured hotkey strings to pynput keyboard objects.

Responsibility:
    Provide a small, isolated adapter that translates persisted string
    representations of hotkeys into `pynput.keyboard` key / chord
    definitions that the hotkey controller can use.

Interface:
    * map_hotkey_string(hotkey_str: str, keyboard_module) -> HotkeyDefinition

Currently supported values (by config `UserConfig.hot_key`):
    * "ctrl_l"   - left control key
    * "ctrl left" - legacy alias for left control; normalized to "ctrl_l"
    * "cmd+ctrl" - command + control chord (either side where available)

Unknown values gracefully fall back to the default single-key ctrl hotkey.
"""

from dataclasses import dataclass
from typing import Iterable, Set, Any


@dataclass(frozen=True)
class HotkeyDefinition:
    """Value object describing a configured hotkey.

    Attributes:
        type: "single" for a single key, "chord" for a simultaneous key combo.
        keys: For "single", a singleton set containing the trigger key.
              For "chord", a set containing all keys that must be held.
    """

    type: str  # "single" | "chord"
    keys: Set[Any]


_DEFAULT_HOTKEY_STRING = "ctrl_l"


def _ctrl_hotkey(keyboard_module: Any) -> HotkeyDefinition:
    key = getattr(keyboard_module.Key, "ctrl_l", getattr(keyboard_module.Key, "ctrl"))
    return HotkeyDefinition(type="single", keys={key})


def _cmd_ctrl_chord(keyboard_module: Any) -> HotkeyDefinition:
    """Define a cmd+ctrl chord.

    On macOS, `pynput` exposes `Key.cmd` / `Key.cmd_l` / `Key.cmd_r` depending
    on the platform / version. To be robust, we include any attributes that
    exist as valid "cmd" keys so that holding either side still works.
    """

    key_candidates: Iterable[str] = ("cmd", "cmd_l", "cmd_r")
    cmd_keys: Set[Any] = set()
    for attr in key_candidates:
        if hasattr(keyboard_module.Key, attr):
            cmd_keys.add(getattr(keyboard_module.Key, attr))

    # Fallback: if for some reason we couldn't find a cmd key, just
    # fall back to ctrl-only single hotkey behaviour.
    if not cmd_keys:
        return _ctrl_hotkey(keyboard_module)

    all_keys: Set[Any] = set(cmd_keys)
    ctrl_key = getattr(
        keyboard_module.Key, "ctrl_l", getattr(keyboard_module.Key, "ctrl")
    )
    all_keys.add(ctrl_key)

    return HotkeyDefinition(type="chord", keys=all_keys)


def map_hotkey_string(hotkey_str: str, keyboard_module: Any) -> HotkeyDefinition:
    "Map a persisted hotkey string to a `HotkeyDefinition"

    normalized = (hotkey_str or _DEFAULT_HOTKEY_STRING).strip().lower()

    if normalized == "ctrl_l":
        return _ctrl_hotkey(keyboard_module)

    if normalized == "cmd+ctrl":
        return _cmd_ctrl_chord(keyboard_module)

    # Unknown value: fallback to the default
    return _ctrl_hotkey(keyboard_module)

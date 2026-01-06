from __future__ import annotations

"""Helpers for mapping configured hotkey strings to pynput keyboard objects."""

from dataclasses import dataclass
from typing import Set, Any


@dataclass(frozen=True)
class HotkeyDefinition:
    """Describes a hotkey: type ('single' or 'chord') and set of keys."""

    type: str
    keys: Set[Any]


_DEFAULT_HOTKEY_STRING = "ctrl_l"


def _ctrl_hotkey(keyboard_module: Any) -> HotkeyDefinition:
    """Single-key left control (or ctrl fallback)."""
    key = getattr(keyboard_module.Key, "ctrl_l", getattr(keyboard_module.Key, "ctrl"))
    return HotkeyDefinition(type="single", keys={key})


def _cmd_ctrl_chord(keyboard_module: Any) -> HotkeyDefinition:
    """Cmd+Ctrl chord using one cmd and one ctrl key."""
    cmd_key = keyboard_module.Key.cmd
    ctrl_key = getattr(keyboard_module.Key, "ctrl_l", keyboard_module.Key.ctrl)
    return HotkeyDefinition(type="chord", keys={cmd_key, ctrl_key})


def map_hotkey_string(hotkey_str: str, keyboard_module: Any) -> HotkeyDefinition:
    """Map config string to HotkeyDefinition."""

    normalized = (hotkey_str or _DEFAULT_HOTKEY_STRING).strip().lower()

    if normalized == "ctrl_l":
        return _ctrl_hotkey(keyboard_module)

    if normalized == "cmd+ctrl":
        return _cmd_ctrl_chord(keyboard_module)

    return _ctrl_hotkey(keyboard_module)

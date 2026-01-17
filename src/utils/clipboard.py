from __future__ import annotations

import subprocess
import sys
from typing import Final, Optional


_PBCOPY_CMD: Final[list[str]] = ["pbcopy"]
_PBPASTE_CMD: Final[list[str]] = ["pbpaste"]

# Holds the clipboard contents observed right before the last set_text call.
_previous_clipboard: Optional[str] = None


def _ensure_macos() -> None:
    if sys.platform != "darwin":
        raise RuntimeError("Clipboard operations are only implemented for macOS (darwin)")


def _read_current_clipboard(*, timeout_seconds: float = 2.0) -> str:
    """Read current clipboard via pbpaste."""
    _ensure_macos()
    out = subprocess.check_output(_PBPASTE_CMD, timeout=timeout_seconds)
    return out.decode("utf-8")


def _write_clipboard(text: str, *, timeout_seconds: float = 2.0) -> None:
    """Write text to clipboard via pbcopy without touching _previous_clipboard."""
    _ensure_macos()
    proc = subprocess.Popen(_PBCOPY_CMD, stdin=subprocess.PIPE)
    if proc is None or proc.stdin is None:
        raise RuntimeError("Failed to launch pbcopy")
    proc.stdin.write(text.encode("utf-8"))
    proc.stdin.close()
    proc.wait(timeout=timeout_seconds)


def set_text(text: str, *, timeout_seconds: float = 2.0) -> None:
    """Set system clipboard contents to `text`.

    Captures the current clipboard contents first and stores in _previous_clipboard,
    then writes the new text.
    """
    _ensure_macos()
    global _previous_clipboard
    try:
        _previous_clipboard = _read_current_clipboard(timeout_seconds=timeout_seconds)
    except Exception:
        # If we can't read, leave previous as None to avoid restoring garbage.
        _previous_clipboard = None
    _write_clipboard(text, timeout_seconds=timeout_seconds)


def clear(*, timeout_seconds: float = 2.0) -> None:
    """Restore the clipboard to the previous value captured before last set_text.

    If no previous value is known, behaves as a no-op.
    """
    _ensure_macos()
    if _previous_clipboard is None:
        return
    # Restore previous without overwriting the saved state; if desired, we could
    # reset _previous_clipboard after restoration.
    _write_clipboard(_previous_clipboard, timeout_seconds=timeout_seconds)

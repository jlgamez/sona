from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List

_AUDIO_SECTION_MARKER = "AVFoundation audio devices:"
_VIDEO_SECTION_MARKER = "AVFoundation video devices:"
_DEVICE_LINE = re.compile(r"\]\s+\[(\d+)\]\s+(.+?)\s*$")


@dataclass(frozen=True)
class AudioDevice:
    """Responsibility: describe one audio input device reported by FFmpeg.

    Interface: ``index`` (unstable, changes as devices connect) and ``name``
    (stable, used to select the device).
    """

    index: int
    name: str


def parse_avfoundation_audio_devices(ffmpeg_stderr: str) -> List[AudioDevice]:
    """Extract audio devices from `-list_devices` output of the avfoundation input."""
    devices: List[AudioDevice] = []
    in_audio_section = False
    for line in ffmpeg_stderr.splitlines():
        if _AUDIO_SECTION_MARKER in line:
            in_audio_section = True
            continue
        if _VIDEO_SECTION_MARKER in line:
            in_audio_section = False
            continue
        if not in_audio_section:
            continue
        # Device lines look like: "[AVFoundation indev @ 0x...] [0] MacBook Pro Microphone"
        match = _DEVICE_LINE.search(line)
        if match:
            devices.append(AudioDevice(index=int(match.group(1)), name=match.group(2)))
    return devices


def list_audio_devices(
    ffmpeg_path: Path, timeout_seconds: float = 5.0
) -> List[AudioDevice]:
    """List audio input devices. Returns an empty list when unsupported or on failure."""
    if sys.platform != "darwin":
        return []
    try:
        # FFmpeg exits non-zero after listing because the empty input fails to open.
        result = subprocess.run(
            [
                str(ffmpeg_path),
                "-hide_banner",
                "-f",
                "avfoundation",
                "-list_devices",
                "true",
                "-i",
                "",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            text=True,
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    return parse_avfoundation_audio_devices(result.stderr)

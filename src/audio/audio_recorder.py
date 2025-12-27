from __future__ import annotations

from pathlib import Path
from typing import Protocol


class AudioRecorder(Protocol):
    """AudioRecorder

    Responsibility:
        Defines a high-level, implementation-agnostic contract for capturing
        short-lived audio segments that can be fed into a transcription
        pipeline. Implementations may use external tools (e.g., ``ffmpeg`` via
        subprocess) or in-process recording libraries, but those details are
        intentionally hidden behind this interface.

    Interface:
        The recorder is designed with a simple lifecycle suitable for
        "push-to-talk" style usage:

        * ``start()`` begins capturing audio from the configured input device.

        * ``stop()`` finalizes the current capture session and returns a
          :class:`pathlib.Path` pointing to the recorded audio file on disk.
          Implementations should use atomic, uniquely named temporary files
          (e.g., incorporating a UUID) to avoid collisions when multiple
          recordings occur in quick succession.

        * ``discard()`` (optional but recommended) allows callers to cancel the
          current recording and clean up any temporary resources without
          producing a file. This is useful when the user taps the hotkey too
          quickly or cancels mid-recording.

        Implementations should:
        * Be safe to use from a hotkey listener thread by keeping ``start`` and
          ``stop`` operations fast and delegating heavy work (e.g., encoding)
          to subprocesses or background workers.
        * Manage the lifecycle of any underlying subprocesses explicitly,
          ensuring they are terminated on normal shutdown or error conditions.
        * Integrate cleanly with singleton-style management so that only a
          single recorder instance owns access to the microphone at a time.
    """

    def start(self) -> None:
        """Begin capturing audio from the configured input source.

        Implementations should return immediately after initiating capture and
        must not block the calling thread for the duration of the recording.
        Any necessary initialization of external tools (e.g., spawning an
        FFmpeg subprocess) should be handled here.
        """

    def stop(self) -> Path:
        """Stop capturing audio and return the path to the recorded file.

        The returned path should point to a fully written, ready-to-read audio
        file compatible with downstream transcription tooling (e.g., Whisper).
        Implementations are responsible for ensuring that the file is flushed
        and closed before this method returns.
        """

    def discard(self) -> None:
        """Cancel the current recording and clean up temporary resources.

        After this call, no audio file should be produced for the in-progress
        recording session. This method should be idempotent so that calling it
        multiple times does not raise errors.
        """

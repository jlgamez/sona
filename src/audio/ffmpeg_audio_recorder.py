from __future__ import annotations

import atexit
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .audio_recorder import AudioRecorder


class FfmpegAudioRecorder(AudioRecorder):
    """Records microphone audio to a temporary file using FFmpeg.

    This class provides a concrete implementation of the AudioRecorder interface
    for capturing short audio clips from the user's default microphone. It uses
    the FFmpeg command-line tool to record audio in a background process and
    saves the result as a temporary file suitable for transcription (e.g., with Whisper).

    Typical usage:
        recorder = FfmpegAudioRecorder(output_dir=Path("/tmp/sona-recordings"))
        recorder.start()   # Begin recording (e.g., on hotkey press)
        ... user speaks ...
        path = recorder.stop()  # Stop recording and get the audio file (e.g., on hotkey release)

    Methods:
        start():
            Starts recording audio from the default input device. This method is non-blocking
            and returns immediately. If a recording is already in progress, calling start() again
            does nothing.
        stop() -> Path:
            Stops the current recording, finalizes the audio file, and returns the path to the file.
            Raises an error if no recording is in progress.
        discard():
            Cancels the current recording and deletes any partial audio file. Safe to call even if
            no recording is active.

    Notes:
        - Each recording is saved to a uniquely named file in the specified output directory.
        - The class ensures that the FFmpeg process is properly terminated and that temporary files
          are cleaned up on errors or when the program exits.
        - Designed for use in push-to-talk workflows, where recording is started and stopped by
          user actions (such as pressing and releasing a hotkey).
    """

    def __init__(
        self,
        output_dir: Path,
        file_extension: str = "wav",
        ffmpeg_executable: str = "ffmpeg",
    ) -> None:
        """Initialize the recorder.

        Args:
            output_dir: Directory in which to place temporary recorded files.
            file_extension: Audio format/extension to use for output files
                (e.g., ``"wav"``). The chosen format must be compatible with
                the downstream transcription pipeline.
            ffmpeg_executable: Name or path of the ``ffmpeg`` executable to
                invoke. Resolved via :func:`shutil.which` for portability.
        """

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)

        resolved = shutil.which(ffmpeg_executable)
        if resolved is None:
            raise RuntimeError(
                f"ffmpeg executable '{ffmpeg_executable}' not found in PATH"
            )

        self._ffmpeg_path: str = resolved
        self._output_dir: Path = output_dir
        self._file_extension: str = file_extension

        self._process: Optional[subprocess.Popen[bytes]] = None
        self._current_temp_audio_file: Optional[Path] = None

        # Ensure any child process is cleaned up on interpreter exit.
        atexit.register(self._cleanup_on_exit)

    def start(self) -> None:
        """Begin capturing audio from the default input device.

        This method spawns a non-blocking ``ffmpeg`` subprocess that writes
        raw audio data to a uniquely named temporary file. If a recording is
        already in progress, the call is treated as a no-op to keep behavior
        idempotent.
        """

        if self._process is not None:
            # Already recording; avoid starting another process.
            return

        from uuid import uuid4

        self._current_temp_audio_file = self._output_dir / f"{uuid4()}.{self._file_extension}"

        input_args = self._build_input_args()

        cmd = [
            self._ffmpeg_path,
            *input_args,
            "-y",  # overwrite if a stale file somehow exists
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(self._current_temp_audio_file),
        ]

        self._process = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop(self) -> Path:
        """Stop capturing audio and return the path to the recorded file.

        Raises:
            RuntimeError: If no recording is currently in progress or if the
                expected output file is missing after the process is stopped.
        """

        if self._process is None:
            return None

        # gracefully terminate ffmpeg process
        self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._process.kill()

        output_path = self._current_temp_audio_file
        self._process = None
        self._current_temp_audio_file = None

        # check if recording was too short (file wasn't created)
        if not output_path.exists():
            return None

        # check if file was created but content was empty
        if output_path.stat().st_size == 0:
            output_path.unlink()
            return None

        return output_path

    def discard(self) -> None:
        """Cancel the current recording and delete any partial file.
        This method is idempotent: calling it when no recording is in progress
        is a no-op.
        """
        if self._process is None:
            return

        print("Discarding current recording...")

        process = self._process
        output_path = self._current_temp_audio_file

        self._process = None
        self._current_temp_audio_file = None

        process.terminate()

        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

        if output_path is not None and output_path.exists():
            try:
                output_path.unlink()
            except OSError:
                # Best-effort cleanup; failures are logged elsewhere if needed.
                pass

    def _cleanup_on_exit(self) -> None:
        """Best-effort cleanup hook for interpreter shutdown.

        Ensures that any child ``ffmpeg`` process is terminated and that any
        partially written file is removed.
        """

        try:
            self.discard()
        except Exception:
            # Avoid raising during interpreter shutdown.
            pass

    def _build_input_args(self) -> list[str]:
        """Build platform-specific ffmpeg input arguments.

        Returns:
            A list of command-line arguments that configure ``ffmpeg`` to read
            from the default audio input device on the current platform.
        """

        if sys.platform == "darwin":
            #TODO In my case the default mic in Mac is :1 but we need a way to determine the default mic programatically
            return ["-f", "avfoundation", "-i", ":1"]

        if sys.platform.startswith("win"):
            # Windows: DirectShow default audio device.
            return ["-f", "dshow", "-i", "audio=default"]

        # Linux/other UNIX: ALSA default device.
        return ["-f", "alsa", "-i", "default"]

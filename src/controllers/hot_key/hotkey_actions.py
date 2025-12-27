from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.audio.audio_recorder import AudioRecorder
from src.controllers.transcription.background_transcription_orchestrator import (
    BackgroundTranscriptionOrchestrator,
)


class HotKeyActions:
    """Coordinate hotkey press/release events with an audio recorder.

    Responsibility:
        Provide concrete callback methods that can be wired directly into a
        :class:`HotkeyController` implementation (e.g., ``PynputHotkeyController``).
        The press handler starts recording; the release handler stops recording
        and forwards the resulting audio file to a downstream consumer.

    Interface:
        Initialize with an ``AudioRecorder`` instance. The public methods
        ``on_press`` and ``on_release`` are lightweight and safe to call from
        a hotkey listener thread. The optional ``cancel`` method allows
        higher-level coordination code to discard an in-flight recording when
        needed (e.g., on errors or aborted interactions). Downstream handling
        of the recorded audio is encapsulated in ``_on_audio_ready`` to avoid
        passing extra callbacks.
    """

    def __init__(
        self,
        recorder: Optional[AudioRecorder],
        orchestrator: Optional[BackgroundTranscriptionOrchestrator] = None,
    ) -> None:
        self._recorder = recorder
        self._orchestrator = orchestrator
        self._is_recording = False

    def on_press(self) -> None:
        """Start recording on hotkey press, guarding against double-starts."""
        if self._is_recording:
            return
        print("Recording started.")
        self._recorder.start()
        self._is_recording = True

    def on_release(self) -> None:
        """Stop recording on hotkey release and forward the audio path."""
        if not self._is_recording:
            return
        print("Recording stopped.")
        self._is_recording = False
        try:
            audio_path = self._recorder.stop()
        except Exception:
            # Best-effort cleanup if stop fails; keep listener thread resilient.
            try:
                self._recorder.discard()
            except Exception:
                pass
            raise
        # Invoke internal handler for downstream processing.
        self._on_audio_ready(audio_path)

    def cancel(self) -> None:
        """Discard an in-flight recording without producing a file."""
        if not self._is_recording:
            return
        self._is_recording = False
        try:
            self._recorder.discard()
        except Exception:
            pass

    def _on_audio_ready(self, path: Path) -> None:
        """Handle the recorded audio file.

        This private hook centralizes the next steps once audio is ready,
        without requiring callers to pass additional callbacks. Keep this
        method lightweight; defer heavy CPU/GPU work to a background worker
        if hotkey latency is a concern. When provided, a
        BackgroundTranscriptionOrchestrator should be used to enqueue the
        work non-blockingly.

        TODO (natural-language plan per 10X standards):
        - Validate that ``path`` exists and points to a readable audio file.
        - Detect best inference device: prefer "mps" on Apple Silicon, then
          "cuda" if available, else fallback to "cpu".
        - Lazily load the Whisper model (do NOT load at app startup). Cache it
          as a singleton so subsequent calls reuse the model.
        - Use fp16=True when supported by the selected device to reduce memory
          and improve speed; fallback to fp16=False otherwise.
        - Read the audio efficiently: for small clips, consider memory-mapping
          or in-memory buffering; otherwise pass the file path to Whisper.
        - Run transcription in a background thread/process to avoid blocking
          the hotkey listener thread.
        - On success: capture the transcribed text; immediately free any
          temporary buffers and delete the temporary audio file to reclaim disk
          space.
        - On failure: log errors with clear context (e.g., permission issues,
          missing ffmpeg, device errors); ensure resources are cleaned up.
        - Optionally, send the transcribed text to the clipboard/paste layer
          (abstracted per platform) or back into the app's event bus.
        """
        if self._orchestrator is not None:
            self._orchestrator.submit(path)
            return
        # Intentionally left empty: implement actual transcription wiring in a
        # background worker adhering to separation of concerns.

    def on_press_test(self) -> None:
        """Temporary tracer: log hotkey press without using the recorder.

        This helper is intended purely for wiring tests. It does not start
        recording or touch the :class:`AudioRecorder`; it only prints a
        message so you can verify that the hotkey callback is being fired.
        """
        print("[TRACE] HotKeyActions.on_press_test -> hotkey press captured.")

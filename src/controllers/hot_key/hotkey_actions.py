from __future__ import annotations

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
        recorder: AudioRecorder,
        orchestrator:BackgroundTranscriptionOrchestrator,
    ) -> None:
        self._recorder = recorder
        self._transcription_orchestrator = orchestrator
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
            self._transcription_orchestrator.attempt_transcription(audio_path)
        except Exception:
            # Best-effort cleanup if stop fails; keep listener thread resilient.
            try:
                print("Recording failed; discarding audio file.")
                self._recorder.discard()
            except Exception:
                pass
            raise

    def cancel(self) -> None:
        """Discard an in-flight recording without producing a file."""
        if not self._is_recording:
            return
        self._is_recording = False
        try:
            self._recorder.discard()
        except Exception:
            pass

"""Audio Recorder CLI Test Script.

This script allows manual testing of the FfmpegAudioRecorder implementation.
Type 'start' to begin recording, 'stop' to end and save, and 'discard' to cancel.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from src.audio.audio_loader import AudioValidatorImpl
from src.audio.ffmpeg_audio_recorder import FfmpegAudioRecorder
from src.controllers.hot_key.hotkey_actions import HotKeyActions
from src.controllers.hot_key.hotkey_controller_impl import HotKeyControllerImpl
from src.controllers.transcription.background_transcription_orchestrator import BackgroundTranscriptionOrchestratorImpl
from src.controllers.transcription.cleanup_service import CleanupServiceImpl
from src.controllers.transcription.model_adapter import ModelAdapterImpl
from src.controllers.transcription.transcription_result_handler import TranscriptionResultHandlerImpl
from src.utils.ffmpeg_utils import resolve_ffmpeg_executable


def main() -> None:

    ffmpeg_executable = resolve_ffmpeg_executable()
    if ffmpeg_executable is None:
        print(
            "Error: ffmpeg executable not found.\n"
            "Please download ffmpeg from https://www.ffmpeg.org/download.html\n"
            "Place the executable in the project root directory",
            file=sys.stderr,
        )
        sys.exit(1)

    temp_audio_directory = Path(__file__).parent / "audio" / "resources" / "temp_audio"

    recorder = FfmpegAudioRecorder(
        output_dir=temp_audio_directory,
        ffmpeg_executable=str(ffmpeg_executable),
    )

    transcription_orchestrator = BackgroundTranscriptionOrchestratorImpl(
        AudioValidatorImpl(),
        ModelAdapterImpl(),
        CleanupServiceImpl(),
        TranscriptionResultHandlerImpl(),
    )

    hot_key_actions = HotKeyActions(recorder=recorder, orchestrator=transcription_orchestrator)
    hot_key_controller = HotKeyControllerImpl(hot_key_actions=hot_key_actions)
    hot_key_controller.start_listening()
    print("Hotkey listener started. Press Ctrl+Left to record.")

    # Keep main thread alive so the background listener can run.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down hotkey listener...")


if __name__ == "__main__":
    main()

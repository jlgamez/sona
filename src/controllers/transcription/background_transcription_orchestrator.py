from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable
from concurrent.futures import ThreadPoolExecutor
import atexit

from src.audio.audio_loader import AudioValidator, AudioValidatorImpl
from .model_adapter import ModelAdapter, ModelAdapterImpl
from .cleanup_service import CleanupService, CleanupServiceImpl
from .transcription_result_handler import TranscriptionResultHandler, TranscriptionResultHandlerImpl
from .device_selector import DeviceSelectorImpl


@runtime_checkable
class BackgroundTranscriptionOrchestrator(Protocol):
    """BackgroundTranscriptionOrchestrator

    Responsibility:
        Coordinate background transcription off the hotkey thread. Internally
        compose AudioValidator, ModelAdapter, CleanupService, and
        TranscriptionResultHandler. Ensure cleanup on success and error.

    Interface:
        * attempt_transcription(path: Path) -> None
        * shutdown() -> None
    """

    def attempt_transcription(self, path: Path) -> None:
        """Enqueue transcription for the given audio file path."""

    def shutdown(self) -> None:
        """Tear down worker resources (threads/processes) at application exit."""


class BackgroundTranscriptionOrchestratorImpl(BackgroundTranscriptionOrchestrator):
    """BackgroundTranscriptionOrchestratorImpl

    Responsibility:
        Concrete implementation that coordinates background transcription using
        a thread pool executor. Composes all transcription components and ensures
        proper cleanup on success and error. Prevents blocking the hotkey thread.

    Interface:
        * attempt_transcription(path: Path) -> None: Enqueue transcription task
        * shutdown() -> None: Clean shutdown of worker threads
    """

    def __init__(
        self,
        audio_loader: AudioValidator,
        model_adapter: ModelAdapter,
        cleanup_service: CleanupService,
        result_handler: TranscriptionResultHandler,
        max_workers: int = 1
    ):
        """Initialize the orchestrator with all required components.

        Args:
            audio_loader: Component to validate audio files. Defaults to AudioValidatorImpl.
            model_adapter: Component to transcribe audio. Defaults to ModelAdapterImpl.
            cleanup_service: Component to clean up resources. Defaults to CleanupServiceImpl.
            result_handler: Component to handle results. Defaults to TranscriptionResultHandlerImpl.
            max_workers: Maximum number of worker threads. Default is 1 to avoid GIL contention.
        """
        self._audio_loader = audio_loader or AudioValidatorImpl()
        self._model_adapter = model_adapter or ModelAdapterImpl(DeviceSelectorImpl())
        self._cleanup_service = cleanup_service or CleanupServiceImpl()
        self._result_handler = result_handler or TranscriptionResultHandlerImpl()

        # Use single worker to avoid GIL contention and model thread-safety issues
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="transcription")

        # Register shutdown hook to ensure cleanup on app exit
        atexit.register(self.shutdown)

    def attempt_transcription(self, path: Path) -> None:
        """Enqueue transcription for the given audio file path.

        Args:
            path: Path to the audio file to transcribe
        """
        self._executor.submit(self._transcribe_task, path)

    def _transcribe_task(self, path: Path) -> None:
        """Execute the transcription task with full error handling and cleanup.

        Args:
            path: Path to the audio file to transcribe
        """
        try:
            # Step 1: Validate audio file (existence, readability, non-empty)
            self._audio_loader.validate(path)

            # Step 2: Transcribe using the file Path (Whisper reads from disk)
            result = self._model_adapter.transcribe(path)

            # Step 3: Extract text from result
            text = result.get("text", "").strip()

            # Step 4: Handle success
            self._result_handler.handle_success(text)

        except Exception as exc:
            # Handle any errors that occur during transcription
            self._result_handler.handle_error(exc)

        finally:
            # Step 5: Cleanup temp file (always runs, even on error)
            try:
                self._cleanup_service.delete_file(path)
            except Exception as cleanup_exc:
                # Log cleanup errors but don't propagate
                print(f"[WARNING] Cleanup error: {cleanup_exc}")

    def shutdown(self) -> None:
        """Tear down worker resources (threads/processes) at application exit.
        Waits for pending tasks to complete before shutting down.
        """
        try:
            self._executor.shutdown(wait=True, cancel_futures=False)
            print("[DEBUG] BackgroundTranscriptionOrchestrator shutdown complete")
        except Exception as e:
            print(f"[WARNING] Error during orchestrator shutdown: {e}")

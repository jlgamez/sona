from __future__ import annotations

from dataclasses import dataclass
from threading import RLock, Thread
from typing import Optional

from src.AppServices import AppServices
from src.core.hot_key.hotkey_controller import HotkeyController
from src.core.transcription.background_transcription_orchestrator import (
    BackgroundTranscriptionOrchestratorImpl,
)


@dataclass
class RuntimeState:
    orchestrator: BackgroundTranscriptionOrchestratorImpl
    hotkey_controller: HotkeyController
    hotkey_thread: Thread


class AudioTranscriptionRuntimeManager:
    """Own the lifecycle of the hotkey listener + transcription orchestrator."""

    def __init__(self, app_services: AppServices) -> None:
        self._app_services = app_services
        self._lock = RLock()
        self._state: Optional[RuntimeState] = None

    def start(self) -> None:
        with self._lock:
            if self._state is not None:
                return
            self._state = self._create_state()
            self._state.hotkey_thread.start()

    def reload(self) -> None:
        with self._lock:
            self._teardown_locked()
            self._state = self._create_state()
            self._state.hotkey_thread.start()

    def stop(self) -> None:
        with self._lock:
            self._teardown_locked()
            self._state = None

    def current_state(self) -> Optional[RuntimeState]:
        with self._lock:
            return self._state

    def _create_state(self) -> RuntimeState:
        orchestrator = self._app_services.create_transcription_orchestrator()
        hotkey_controller = self._app_services.create_hot_key_controller(orchestrator)
        hotkey_thread = Thread(
            target=hotkey_controller.start_listening,
            name="HotkeyListenerThread",
            daemon=True,
        )
        return RuntimeState(
            orchestrator=orchestrator,
            hotkey_controller=hotkey_controller,
            hotkey_thread=hotkey_thread,
        )

    def _teardown_locked(self) -> None:
        if self._state is None:
            return
        stop_listening = getattr(self._state.hotkey_controller, "stop_listening", None)
        if callable(stop_listening):
            stop_listening()
        if self._state.hotkey_thread.is_alive():
            self._state.hotkey_thread.join(timeout=1.0)
        shutdown = getattr(self._state.orchestrator, "shutdown", None)
        if callable(shutdown):
            shutdown()

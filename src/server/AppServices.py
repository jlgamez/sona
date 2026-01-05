from pathlib import Path
from threading import Thread
from typing import Optional

from src.audio.audio_validator import AudioValidatorImpl
from src.audio.audio_recorder_impl import AudioRecorderImpl
from src.controllers.hot_key.hotkey_actions import HotKeyActions
from src.controllers.hot_key.hotkey_controller import HotkeyController
from src.controllers.hot_key.hotkey_controller_impl import HotKeyControllerImpl
from src.controllers.transcription.background_transcription_orchestrator import (
    BackgroundTranscriptionOrchestratorImpl,
)
from src.controllers.transcription.cleanup_service import CleanupServiceImpl
from src.controllers.transcription.model_adapter import ModelAdapterImpl
from src.controllers.transcription.transcription_result_handler import (
    TranscriptionResultHandlerImpl,
)
from src.server.config.serivce.config_loading_service import ConfigLoadingService
from src.server.hot_key.service.hot_key_service import HotKeyService
from src.server.models.service.local_model_service import LocalModelService
from src.utils.bundled_ffmpeg import get_bundled_ffmpeg


class AppServices:
    TEMP_AUDIO_DIRECTORY: Path = Path("src") / "audio" / "resources" / "temp_audio"

    _recorder: AudioRecorderImpl
    _transcription_orchestrator: BackgroundTranscriptionOrchestratorImpl
    _hot_key_controller: HotkeyController
    _hot_key_thread: Thread
    _config_loader: ConfigLoadingService
    _hot_key_service: HotKeyService

    @classmethod
    def initialise_services(
        cls,
        repo_root: Path,
        config_loader: ConfigLoadingService,
        hot_key_service: HotKeyService,
    ):
        ffmpeg_executable = get_bundled_ffmpeg(repo_root)
        temp_audio_directory = repo_root / cls.TEMP_AUDIO_DIRECTORY

        # Require explicit config loader injection
        cls._config_loader = config_loader
        cls._hot_key_service = hot_key_service

        # audio recorder service
        cls._recorder = AudioRecorderImpl(
            output_dir=temp_audio_directory, ffmpeg_executable=str(ffmpeg_executable)
        )

        # transcription orchestrator service
        cls._transcription_orchestrator = cls._initialise_transcription_orchestrator()

        # hotkey controller service
        cls._hot_key_controller = cls._initialise_hot_key_controller()

        # start a hotkey listener thread
        if not cls._is_active_hot_key_thread():
            cls._start_hot_key_thread_with(cls._hot_key_controller)

    @classmethod
    def _initialise_transcription_orchestrator(cls):
        return BackgroundTranscriptionOrchestratorImpl(
            AudioValidatorImpl(),
            ModelAdapterImpl(),
            CleanupServiceImpl(),
            TranscriptionResultHandlerImpl(),
        )

    @classmethod
    def _initialise_hot_key_controller(cls):
        hot_key_actions = HotKeyActions(
            recorder=cls._recorder, orchestrator=cls._transcription_orchestrator
        )
        # Use the injected config loader to obtain the configured hotkey.
        user_config = cls._config_loader.load_config()
        resolved_hot_key = cls._resolve_hot_key_string(user_config.hot_key)
        return HotKeyControllerImpl(
            hot_key_actions=hot_key_actions,
            hotkey_str=resolved_hot_key,
        )

    @classmethod
    def _resolve_hot_key_string(cls, configured_hot_key: str | None) -> str:
        configured_key = (configured_hot_key or "").strip().lower()
        available_hot_keys = cls._hot_key_service.list_hot_keys()
        for option in available_hot_keys:
            if option.name.lower() == configured_key:
                return option.name
        default_option = cls._hot_key_service.get_default_hot_key()
        if default_option is not None:
            return default_option.name
        if available_hot_keys:
            return available_hot_keys[0].name
        return "ctrl_l"

    @classmethod
    def _is_active_hot_key_thread(cls):
        thread = getattr(cls, "_hot_key_thread", None)
        return thread is not None and thread.is_alive()

    @classmethod
    def _start_hot_key_thread_with(cls, hot_key_controller: HotkeyController):
        cls._hot_key_thread = Thread(
            target=hot_key_controller.start_listening,
            name="HotkeyListenerThread",
            daemon=True,
        )
        cls._hot_key_thread.start()

    @classmethod
    def get_recorder(cls) -> AudioRecorderImpl:
        assert cls._recorder is not None, "AppServices.init() must be called first"
        return cls._recorder

    @classmethod
    def get_orchestrator(cls) -> BackgroundTranscriptionOrchestratorImpl:
        assert (
            cls._transcription_orchestrator is not None
        ), "AppServices.init() must be called first"
        return cls._transcription_orchestrator

    @classmethod
    def get_hotkey_controller(cls) -> Optional[HotkeyController]:
        return cls._hot_key_controller

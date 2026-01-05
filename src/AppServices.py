from pathlib import Path

from src.audio.audio_validator import AudioValidatorImpl
from src.audio.audio_recorder_impl import AudioRecorderImpl
from src.controllers.hot_key.hotkey_actions import HotKeyActions
from src.controllers.hot_key.hotkey_controller import HotkeyController
from src.controllers.hot_key.hotkey_controller_impl import HotKeyControllerImpl
from src.controllers.transcription.background_transcription_orchestrator import (
    BackgroundTranscriptionOrchestrator,
    BackgroundTranscriptionOrchestratorImpl,
)
from src.controllers.transcription.cleanup_service import CleanupServiceImpl
from src.controllers.transcription.device_selector import DeviceSelectorImpl
from src.controllers.transcription.model_adapter import ModelAdapterImpl
from src.controllers.transcription.transcription_result_handler import (
    TranscriptionResultHandlerImpl,
)
from src.server.config.serivce.config_load_service import ConfigLoadService
from src.server.hot_key.service.hot_key_service import HotKeyService
from src.utils.bundled_ffmpeg import get_bundled_ffmpeg


class AppServices:
    TEMP_AUDIO_DIRECTORY: Path = Path("src") / "audio" / "resources" / "temp_audio"

    def __init__(
        self,
        repo_root: Path,
        config_loader: ConfigLoadService,
        hot_key_service: HotKeyService,
    ) -> None:
        """Initialize the application services container.

        Args:
            repo_root: Root directory of the project
            config_loader: Service for loading user configuration
            hot_key_service: Service for managing hotkey definitions
        """
        ffmpeg_executable = get_bundled_ffmpeg(repo_root)
        temp_audio_directory = repo_root / self.TEMP_AUDIO_DIRECTORY

        self._config_loader = config_loader
        self._hot_key_service = hot_key_service
        self._recorder = AudioRecorderImpl(
            output_dir=temp_audio_directory,
            ffmpeg_executable=str(ffmpeg_executable),
        )

    def create_transcription_orchestrator(
        self,
    ) -> BackgroundTranscriptionOrchestratorImpl:
        """Create a new transcription orchestrator with current configuration."""
        return BackgroundTranscriptionOrchestratorImpl(
            AudioValidatorImpl(),
            ModelAdapterImpl(
                model_name=self._config_loader.load_config().current_model,
                device_selector=DeviceSelectorImpl(),
            ),
            CleanupServiceImpl(),
            TranscriptionResultHandlerImpl(),
        )

    def create_hot_key_controller(
        self, orchestrator: BackgroundTranscriptionOrchestrator
    ) -> HotkeyController:
        """Create a new hotkey controller with the given orchestrator."""
        hot_key_actions = HotKeyActions(
            recorder=self._recorder, orchestrator=orchestrator
        )
        user_config = self._config_loader.load_config()
        resolved_hot_key = self._resolve_hot_key_string(user_config.hot_key)
        return HotKeyControllerImpl(
            hot_key_actions=hot_key_actions,
            hotkey_str=resolved_hot_key,
        )

    def _resolve_hot_key_string(self, configured_hot_key: str | None) -> str:
        """Resolve a hotkey string to a valid hotkey definition."""
        configured_key = (configured_hot_key or "").strip().lower()
        available_hot_keys = self._hot_key_service.list_hot_keys()
        for option in available_hot_keys:
            if option.name.lower() == configured_key:
                return option.name
        default_option = self._hot_key_service.get_default_hot_key()
        if default_option is not None:
            return default_option.name
        if available_hot_keys:
            return available_hot_keys[0].name
        return "ctrl_l"

    def get_recorder(self) -> AudioRecorderImpl:
        """Get the audio recorder instance."""
        return self._recorder

from pathlib import Path
from typing import List, Optional

from src.audio.audio_devices import AudioDevice, list_audio_devices
from src.audio.audio_validator import AudioValidatorImpl
from src.audio.AudioRecorderImpl import AudioRecorderImpl
from src.core.hot_key.HotKeyActions import HotKeyActions
from src.core.hot_key.HotkeyController import HotkeyController
from src.core.hot_key.HotKeyControllerImpl import HotKeyControllerImpl
from src.core.transcription.AITranscriber import AITranscriberImpl
from src.core.transcription.BackgroundTranscriptionOrchestrator import (
    BackgroundTranscriptionOrchestrator,
    BackgroundTranscriptionOrchestratorImpl,
)
from src.core.transcription.CleanupService import CleanupServiceImpl
from src.core.transcription.TranscriptionResultHandler import (
    TranscriptionResultHandlerImpl,
)
from src.server.config.serivce.ConfigLoadService import ConfigLoadService
from src.server.hot_key.service.HotKeyService import HotKeyService
from src.utils.BundledFfmpeg import get_bundled_ffmpeg


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
        self._ffmpeg_executable = get_bundled_ffmpeg(repo_root)
        self._temp_audio_directory = repo_root / self.TEMP_AUDIO_DIRECTORY

        self._config_loader = config_loader
        self._hot_key_service = hot_key_service

    def create_transcription_orchestrator(
        self,
    ) -> BackgroundTranscriptionOrchestratorImpl:
        """Create a new transcription orchestrator with current configuration."""
        return BackgroundTranscriptionOrchestratorImpl(
            AudioValidatorImpl(),
            AITranscriberImpl(
                model_name=self._config_loader.load_config().current_model,
            ),
            CleanupServiceImpl(),
            TranscriptionResultHandlerImpl(),
        )

    def create_hot_key_controller(
        self, orchestrator: BackgroundTranscriptionOrchestrator
    ) -> HotkeyController:
        """Create a new hotkey controller with the given orchestrator."""
        user_config = self._config_loader.load_config()
        # A new recorder per runtime so a changed microphone applies on reload.
        recorder = AudioRecorderImpl(
            output_dir=self._temp_audio_directory,
            ffmpeg_executable=str(self._ffmpeg_executable),
            input_device=self._resolve_mic_device(user_config.mic_device),
        )
        hot_key_actions = HotKeyActions(recorder=recorder, orchestrator=orchestrator)
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

    def list_audio_devices(self) -> List[AudioDevice]:
        """List the audio input devices currently available."""
        return list_audio_devices(self._ffmpeg_executable)

    def _resolve_mic_device(self, configured_device: Optional[str]) -> Optional[str]:
        """Return the configured microphone, or None (system default) if it is unavailable."""
        if not configured_device:
            return None
        available_names = {device.name for device in self.list_audio_devices()}
        if configured_device in available_names:
            return configured_device
        print(
            f"[WARNING] Microphone '{configured_device}' not found; using system default."
        )
        return None

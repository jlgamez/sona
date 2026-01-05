from typing import Dict, Any

from src.server.config.entity.user_config import (
    ClipboardBehaviour,
    UserConfig,
)
from src.server.config.repository.config_repository import ConfigRepository
from src.server.config.serivce.config_loading_service import ConfigLoadingService


class ConfigLoaderServiceImpl(ConfigLoadingService):
    def __init__(self, config_repository: ConfigRepository, defaults: dict):
        self._config_repository = config_repository
        self._defaults = defaults

    def load_config(self) -> UserConfig:
        """Load config from disk or return defaults if missing/invalid."""
        raw_data = self._config_repository.read_user_config()
        if not raw_data:
            return self._default_config()

        return self._parse_config(raw_data)

    def _parse_config(self, data: Dict[str, Any]) -> UserConfig:
        """Parse a raw dict into a UserConfig entity."""
        return UserConfig(
            hot_key=data.get("hot_key", "ctrl_l"),
            intelligent_mode=bool(data.get("intelligent_mode", True)),
            text_selection_awareness=bool(data.get("text_selection_awareness", True)),
            clipboard_behaviour=self._parse_clipboard_behaviour(data),
            current_model=data.get("current_model", "default"),
        )

    def _parse_clipboard_behaviour(self, data: Dict[str, Any]) -> ClipboardBehaviour:
        """Extract and parse clipboard_behaviour from raw config data."""
        clipboard_data = data.get("clipboard_behaviour", {}) or {}
        return ClipboardBehaviour(
            autonomous_pasting=clipboard_data.get("autonomous_pasting", False),
            keep_output_in_clipboard=clipboard_data.get(
                "keep_output_in_clipboard", True
            ),
        )

    def _default_config(self) -> UserConfig:
        """Return a default UserConfig with sensible defaults."""
        return UserConfig(
            hot_key=self._defaults["hot_key"], current_model=self._defaults["model"]
        )

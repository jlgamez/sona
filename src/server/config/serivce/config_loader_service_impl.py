import json
from typing import Dict, Any

from src.server.config.entity.user_config import (
    ClipboardBehaviour,
    UserConfig,
)
from src.server.config.serivce.config_loading_service import ConfigLoadingService
from src.server.config.serivce.constants import CONFIG_PATH


class ConfigLoaderServiceImpl(ConfigLoadingService):

    def load_config(self) -> UserConfig:
        """Load config from disk or return defaults if missing/invalid."""
        raw_data = self._read_config_file()
        if not raw_data:
            return self._default_config()

        return self._parse_config(raw_data)

    def _read_config_file(self) -> Dict[str, Any] | None:
        """Read and parse the JSON config file. Returns None on any error."""
        try:
            if not CONFIG_PATH.exists():
                return None
            with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
                data = json.load(config_file)
            if not isinstance(data, dict):
                return None
            return data
        except Exception:
            return None

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
        return UserConfig()

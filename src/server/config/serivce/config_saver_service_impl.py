import json
from pathlib import Path
from dataclasses import asdict

from src.server.config.entity.user_config import UserConfig
from src.server.config.serivce.config_saving_service import ConfigSavingService
from src.server.config.serivce.constants import CONFIG_PATH
from src.server.user_config_service import CONFIG_DIR


class ConfigSaverServiceImpl(ConfigSavingService):
    """Implementation for persisting UserConfig to JSON on disk."""

    def save_user_config(self, config: UserConfig) -> bool:
        try:
            # Ensure config directory exists
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            # Convert dataclass to dict
            config_dict = asdict(config)

            # Write to temp file first for atomic operation
            temp_path = CONFIG_PATH.with_suffix(".tmp")
            with temp_path.open("w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            # Atomic rename
            temp_path.replace(CONFIG_PATH)
            return True

        except Exception as e:
            # Log error in production; for now just return False
            print(f"Failed to save config: {e}")
            return False

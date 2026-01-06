import json
from dataclasses import asdict

from src.server.config.entity.user_config import UserConfig
from src.server.config.repository.config_repository import ConfigRepository
from src.server.config.serivce.config_saving_service import ConfigSavingService


class ConfigSaverServiceImpl(ConfigSavingService):
    """Implementation for persisting UserConfig to JSON on disk."""

    def __init__(self, config_repository: ConfigRepository):
        self._config_repository = config_repository

    def save_user_config(self, config: UserConfig) -> bool:
        try:
            # Convert dataclass to dict
            config_dict = asdict(config)

            return self._config_repository.write_user_config(config_dict)

        except Exception as e:
            # Log error in production; for now just return False
            print(f"Failed to save config: {e}")
            return False

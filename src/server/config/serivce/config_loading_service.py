from typing import Protocol

from src.server.config.entity.user_config import UserConfig


class ConfigLoadingService(Protocol):

    def load_config(self) -> UserConfig:
        """Load configuration from a source and return it as a UserConfig entity."""
        ...

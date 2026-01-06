from abc import ABC, abstractmethod

from src.server.config.entity.user_config import UserConfig


class ConfigSavingService(ABC):
    """Interface for persisting user configuration to disk."""

    @abstractmethod
    def save_user_config(self, config: UserConfig) -> bool:
        """
        Save the provided UserConfig to persistent storage.

        Args:
            config: The UserConfig object to persist.

        Returns:
            True if save was successful, False otherwise.
        """
        pass

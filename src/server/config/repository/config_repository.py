import json
from asyncio import Protocol
from typing import Any, Dict

from src.server.config.constants import CONFIG_PATH


class ConfigRepository(Protocol):

    def read_user_config(self) -> Dict[str, Any] | None:
        pass


class ConfigRepositoryImpl(ConfigRepository):

    def read_user_config(self) -> Dict[str, Any] | None:
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

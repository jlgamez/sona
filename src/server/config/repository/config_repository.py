import json
from pathlib import Path
from typing import Any, Dict, Protocol


class ConfigRepository(Protocol):

    def read_user_config(self) -> Dict[str, Any] | None:
        pass

    def write_user_config(self, data: Dict[str, Any]) -> bool:
        pass


class ConfigRepositoryImpl(ConfigRepository):

    _CONFIG_DIR = Path.home() / ".sona"
    _CONFIG_PATH = _CONFIG_DIR / "user_config.json"

    def read_user_config(self) -> Dict[str, Any] | None:
        try:
            if not self._CONFIG_PATH.exists():
                return None
            with self._CONFIG_PATH.open("r", encoding="utf-8") as config_file:
                data = json.load(config_file)
            if not isinstance(data, dict):
                return None
            return data
        except Exception:
            return None

    def write_user_config(self, data: Dict[str, Any]) -> bool:
        try:
            self._CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            temp_path = self._CONFIG_PATH.with_suffix(".tmp")
            with temp_path.open("w", encoding="utf-8") as config_file:
                json.dump(data, config_file, indent=2, ensure_ascii=False)
            temp_path.replace(self._CONFIG_PATH)
            return True
        except Exception:
            return False

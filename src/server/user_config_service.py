import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any


CONFIG_DIR = Path.home() / ".sona"
CONFIG_PATH = CONFIG_DIR / "user_config.json"


@dataclass
class ClipboardBehaviour:
    autonomous_pasting: bool = False
    keep_output_in_clipboard: bool = True


@dataclass
class TranscriptionModelInfo:
    name: str
    required_ram: str
    relative_speed: str
    in_system: bool


@dataclass
class UserConfig:
    hot_key: str = "cmd+shift+space"
    intelligent_mode: bool = True
    text_selection_awareness: bool = True
    clipboard_behaviour: ClipboardBehaviour = field(default_factory=ClipboardBehaviour)
    current_model: str = "default"
    all_transcription_models: List[TranscriptionModelInfo] = field(default_factory=list)


def _ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _default_models() -> List[TranscriptionModelInfo]:
    return [
        TranscriptionModelInfo(
            name="tiny",
            required_ram="1GB",
            relative_speed="fast",
            in_system=False,
        ),
        TranscriptionModelInfo(
            name="base",
            required_ram="2GB",
            relative_speed="medium",
            in_system=False,
        ),
    ]


def _default_config() -> UserConfig:
    return UserConfig(all_transcription_models=_default_models())


def _config_from_dict(data: Dict[str, Any]) -> UserConfig:
    clipboard_config_data = data.get("clipboard_behaviour", {}) or {}
    clipboard_behaviour = ClipboardBehaviour(
        autonomous_pasting=clipboard_config_data.get("autonomous_pasting", False),
        keep_output_in_clipboard=clipboard_config_data.get(
            "keep_output_in_clipboard", True
        ),
    )

    models_raw = data.get("all_transcription_models", []) or []
    models: List[TranscriptionModelInfo] = []
    for model in models_raw:
        if not isinstance(model, dict):
            continue
        models.append(
            TranscriptionModelInfo(
                name=model.get("name", "unknown"),
                required_ram=model.get("required_ram", "unknown"),
                relative_speed=model.get("relative_speed", "unknown"),
                in_system=bool(model.get("in_system", False)),
            )
        )

    cfg = UserConfig(
        hot_key=data.get("hot_key", "cmd+shift+space"),
        intelligent_mode=bool(data.get("intelligent_mode", True)),
        text_selection_awareness=bool(data.get("text_selection_awareness", True)),
        clipboard_behaviour=clipboard_behaviour,
        current_model=data.get("current_model", "default"),
        all_transcription_models=models or _default_models(),
    )
    return cfg


def load_config() -> UserConfig:
    """Load config from disk or return defaults if missing/invalid.

    If a LocalModelService is provided, the `all_transcription_models` list in
    the returned config will have its `in_system` flags updated based on the
    current state of the local Whisper cache. Callers do not need to pass any
    specific model names; the models are part of the user config itself.
    """
    try:
        if not CONFIG_PATH.exists():
            config = _default_config()
        else:
            with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
                raw_config_json = json.load(config_file)
            if not isinstance(raw_config_json, dict):
                config = _default_config()
            else:
                config = _config_from_dict(raw_config_json)
    except Exception:
        # On any error, fall back to defaults; callers can decide if they need logging.
        config = _default_config()

    return config


def save_config(partial_update: Dict[str, Any]) -> UserConfig:
    """Merge a partial update into the current config and persist it.

    Returns the updated UserConfig instance.
    """
    _ensure_config_dir()
    current = load_config()
    # Convert to dict structure suitable for merging
    current_dict = to_dict(current)
    current_dict.update(partial_update or {})

    updated = _config_from_dict(current_dict)

    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(to_dict(updated), f, indent=2)

    return updated


def to_dict(config: UserConfig) -> Dict[str, Any]:
    """Convert UserConfig dataclass (with nested types) to a plain dict."""
    data = asdict(config)
    # Ensure keys match desired JSON naming exactly
    # asdict already converts dataclasses recursively, so structure is correct.
    return data


def get_config_dict() -> Dict[str, Any]:
    """Convenience helper to get the current config as a plain dict.

    If a LocalModelService is provided, `all_transcription_models` will have
    `in_system` updated according to the current local Whisper cache.
    """
    return to_dict(load_config())

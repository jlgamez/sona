from dataclasses import dataclass, field
from typing import List


@dataclass
class ClipboardBehaviour:
    autonomous_pasting: bool = True
    keep_output_in_clipboard: bool = True


@dataclass
class TranscriptionModelInfo:
    name: str
    english_only: bool
    required_ram: str
    relative_speed: str
    in_system: bool


@dataclass
class UserConfig:
    hot_key: str = "ctrl left"
    intelligent_mode: bool = False
    text_selection_awareness: bool = False
    clipboard_behaviour: ClipboardBehaviour = field(default_factory=ClipboardBehaviour)
    current_model: str = "turbo"
    available_models: List[TranscriptionModelInfo] = field(default_factory=list)

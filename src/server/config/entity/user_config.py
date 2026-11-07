from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ClipboardBehaviour:
    autonomous_pasting: bool = True
    keep_output_in_clipboard: bool = True


@dataclass
class UserConfig:
    hot_key: str
    current_model: str
    intelligent_mode: bool = False
    text_selection_awareness: bool = False
    clipboard_behaviour: ClipboardBehaviour = field(default_factory=ClipboardBehaviour)
    # Name of the input microphone; None means the system default device.
    mic_device: Optional[str] = None

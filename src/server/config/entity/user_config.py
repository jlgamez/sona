from dataclasses import dataclass, field


@dataclass
class ClipboardBehaviour:
    autonomous_pasting: bool = True
    keep_output_in_clipboard: bool = True


@dataclass
class UserConfig:
    hot_key: str = "ctrl_l"
    intelligent_mode: bool = False
    text_selection_awareness: bool = False
    clipboard_behaviour: ClipboardBehaviour = field(default_factory=ClipboardBehaviour)
    current_model: str = "base.en"

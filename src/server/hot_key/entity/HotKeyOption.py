from dataclasses import dataclass


@dataclass
class HotKeyOption:
    name: str
    display_name: str
    is_default: bool = False

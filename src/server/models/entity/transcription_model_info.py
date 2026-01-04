from dataclasses import dataclass


@dataclass
class TranscriptionModelInfo:
    name: str
    english_only: bool
    required_ram: str
    relative_speed: str
    in_system: bool

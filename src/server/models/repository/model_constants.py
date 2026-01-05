# Model metadata: (filename, english_only, required_ram, relative_speed)
from pathlib import Path
from typing import Final

MODELS_INFO = {
    # Tiny
    "tiny.en": ("tiny.en.pt", True, "~1 GB", "32×"),
    "tiny": ("tiny.pt", False, "~1 GB", "32×"),
    # Base
    "base.en": ("base.en.pt", True, "~1 GB", "16×"),
    "base": ("base.pt", False, "~1 GB", "16×"),
    # Small
    "small.en": ("small.en.pt", True, "~2 GB", "6×"),
    "small": ("small.pt", False, "~2 GB", "6×"),
    # Medium
    "medium.en": ("medium.en.pt", True, "~5 GB", "2×"),
    "medium": ("medium.pt", False, "~5 GB", "2×"),
    # Large variants
    "large-v1": ("large-v1.pt", False, "~10 GB", "1×"),
    "large-v2": ("large-v2.pt", False, "~10 GB", "1×"),
    "large-v3": ("large-v3.pt", False, "~10 GB", "1×"),
    # Turbo
    "large-v3-turbo": ("large-v3-turbo.pt", False, "~6 GB", "8×"),
}

WHISPER_CACHE_DIR: Final[Path] = Path.home() / ".cache" / "whisper"

DEFAULT_MODEL = ("base.en", MODELS_INFO["base.en"])

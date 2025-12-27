import shutil
from pathlib import Path
from typing import Optional


def resolve_ffmpeg_executable() -> Optional[Path]:
    found = shutil.which("ffmpeg")
    if found is not None:
        return Path(found)
    project_root = Path(__file__).resolve().parent.parent.parent
    ffmpeg_executable = project_root / "ffmpeg"
    if ffmpeg_executable.is_file() and ffmpeg_executable.exists():
        return ffmpeg_executable
    return None

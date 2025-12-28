import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


def resolve_ffmpeg_executable() -> Optional[Path]:
    """Resolve ffmpeg executable and ensure it's accessible in PATH.

    Responsibility:
        Locate ffmpeg binary either in system PATH or project root.
        If found in project root, add its directory to PATH so downstream
        tools (like Whisper's audio decoder) can locate it.
        Verify the binary is actually executable.

    Returns:
        Path to ffmpeg executable if found and working, None otherwise.
    """
    # First check if ffmpeg is already in PATH
    found = shutil.which("ffmpeg")
    if found is not None:
        if _test_ffmpeg(Path(found)):
            return Path(found)

    # Check project root for a local ffmpeg binary
    project_root = Path(__file__).resolve().parent.parent.parent
    ffmpeg_executable = project_root / "ffmpeg"

    if ffmpeg_executable.is_file() and ffmpeg_executable.exists():
        # Test if it works
        if not _test_ffmpeg(ffmpeg_executable):
            print(f"[WARNING] ffmpeg binary found but not working: {ffmpeg_executable}")
            return None

        # Add project root to PATH so Whisper can find ffmpeg
        project_root_str = str(project_root)
        current_path = os.environ.get("PATH", "")
        if project_root_str not in current_path:
            os.environ["PATH"] = f"{project_root_str}{os.pathsep}{current_path}"
            print(f"[DEBUG] Added {project_root_str} to PATH for ffmpeg")

        return ffmpeg_executable

    return None


def _test_ffmpeg(ffmpeg_path: Path) -> bool:
    try:
        result = subprocess.run(
            [str(ffmpeg_path), "-version"],
            capture_output=True,
            timeout=5,
            check=False
        )
        return result.returncode == 0
    except Exception:
        return False


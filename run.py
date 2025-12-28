#!/usr/bin/env python3
"""
Entry point for the Sona Audio Recorder CLI.
Ensures the project root is in sys.path and launches the main application logic.
"""
import sys
from pathlib import Path


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    # ensure ffmpeg executable is on PATH
    from src.utils.bundled_ffmpeg import get_bundled_ffmpeg
    get_bundled_ffmpeg(project_root)

    from src.main import main
    main()

if __name__ == "__main__":
    bootstrap()

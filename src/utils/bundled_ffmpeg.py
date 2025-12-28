from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar, Optional


@dataclass(frozen=True, slots=True)
class BundledFfmpeg:
    """
    Responsibility:
        Provide a deterministic, environment-agnostic way to locate and configure the
        project-bundled FFmpeg binary (no system FFmpeg fallback).

    Interface:
        - resolve: returns an absolute Path to the bundled FFmpeg binary.
        - configure_env(ffmpeg_path): mutates env vars so subprocess callers can find FFmpeg.
        - configure(repo_root): one-call resolve + configure; returns the resolved Path.
    """

    env_path_key: str = "PATH"
    env_imageio_key: str = "IMAGEIO_FFMPEG_EXE"
    instance:  ClassVar[Optional["BundledFfmpeg"]] = None

    @classmethod
    def get_instance(cls) -> BundledFfmpeg:
        if cls.instance is None:
            cls.instance = BundledFfmpeg()
        return cls.instance

    def configure(self, repo_root: Path) -> Path:
        ffmpeg_path = self.resolve(repo_root)
        self.configure_env(ffmpeg_path)
        return ffmpeg_path

    def resolve(self, repo_root: Path) -> Path:
        ffmpeg_path = (repo_root.resolve() / "ffmpeg").resolve()

        if not ffmpeg_path.exists():
            raise FileNotFoundError(
                f"Bundled FFmpeg not found at expected path: {ffmpeg_path}"
            )

        return ffmpeg_path

    def configure_env(self, ffmpeg_path: Path) -> None:
        ffmpeg_path = ffmpeg_path.resolve()
        self.ensure_executable(ffmpeg_path)

        os.environ[self.env_imageio_key] = str(ffmpeg_path)

        ffmpeg_dir = ffmpeg_path.parent
        existing_path = os.environ.get(self.env_path_key, "")
        os.environ[self.env_path_key] = f"{ffmpeg_dir}{os.pathsep}{existing_path}"

    def ensure_executable(self, ffmpeg_path: Path) -> None:
        try:
            if not os.access(ffmpeg_path, os.X_OK):
                ffmpeg_path.chmod(0o755)
        except OSError:
            # Do not crash here; the eventual subprocess error will be clearer.
            pass


def get_bundled_ffmpeg(repo_root: Path) -> Path:
    bundled_ffmpeg = BundledFfmpeg.get_instance()
    return bundled_ffmpeg.configure(repo_root)
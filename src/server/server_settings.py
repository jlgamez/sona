from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import List, Optional

DEFAULT_PORT = 5000
DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "null",  # Electron renderer loaded from file://
)


@dataclass(frozen=True)
class ServerSettings:
    """Responsibility: hold the Flask server's network settings.

    Interface: ``host`` (always localhost), ``port`` and ``allowed_origins``.
    Build with ``from_args``; port comes from ``--port``, then ``SONA_PORT``;
    origins come from ``SONA_ALLOWED_ORIGINS`` (comma-separated).
    """

    host: str
    port: int
    allowed_origins: List[str]

    @classmethod
    def from_args(cls, argv: Optional[List[str]] = None) -> ServerSettings:
        parser = argparse.ArgumentParser(description="Sona backend")
        parser.add_argument("--port", type=int, default=None)
        args = parser.parse_args(argv)

        port = args.port
        if port is None:
            env_port = os.environ.get("SONA_PORT")
            try:
                port = int(env_port) if env_port else DEFAULT_PORT
            except ValueError:
                parser.error(f"SONA_PORT must be an integer, got '{env_port}'")
        if not 1 <= port <= 65535:
            parser.error(f"port must be between 1 and 65535, got {port}")

        env_origins = os.environ.get("SONA_ALLOWED_ORIGINS", "")
        origins = [o.strip() for o in env_origins.split(",") if o.strip()]
        return cls(
            host="127.0.0.1",
            port=port,
            allowed_origins=origins or list(DEFAULT_ALLOWED_ORIGINS),
        )

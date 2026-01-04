#!/usr/bin/env python3
"""
Entry point for the Sona Audio Recorder CLI.
Ensures the project root is in sys.path and launches the main application logic.
"""
import sys
from importlib import reload
from pathlib import Path

import ApplicationServices

from src.server.AppServices import AppServices
from src.server.config.serivce.config_loader_service_impl import ConfigLoaderServiceImpl


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    app_services = AppServices()
    app_services.initialise_services(project_root, ConfigLoaderServiceImpl())

    from src.server.app import create_flask_app

    flask_app = create_flask_app()
    flask_app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    bootstrap()

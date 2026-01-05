#!/usr/bin/env python3
"""
Entry point for the Sona Audio Recorder CLI.
Ensures the project root is in sys.path and launches the main application logic.
"""
import sys
from pathlib import Path

from src.server.AppServices import AppServices
from src.server.config.repository.config_repository import ConfigRepositoryImpl
from src.server.config.serivce.config_loader_service_impl import ConfigLoaderServiceImpl
from src.server.hot_key.repository.hot_key_repository import HotKeyRepositoryImpl
from src.server.hot_key.service.hot_key_service import HotKeyServiceImpl
from src.server.models.repository.model_repository import ModelRepositoryImpl
from src.server.models.service.local_model_service import LocalModelServiceImpl


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    hot_key_service = HotKeyServiceImpl(HotKeyRepositoryImpl())
    model_service = LocalModelServiceImpl(ModelRepositoryImpl())
    config_defaults = {
        "hot_key": hot_key_service.get_default_hot_key().name,
        "model": model_service.get_default_model_name(),
    }

    config_loader = ConfigLoaderServiceImpl(ConfigRepositoryImpl(), config_defaults)

    app_services = AppServices()
    app_services.initialise_services(project_root, config_loader, hot_key_service)

    from src.server.app import create_flask_app

    flask_app = create_flask_app()
    flask_app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    bootstrap()

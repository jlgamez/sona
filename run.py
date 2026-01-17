#!/usr/bin/env python3
"""
Entry point for the Sona Audio Recorder CLI.
Ensures the project root is in sys.path and launches the main application logic.
"""
import sys
from pathlib import Path

from src.AppServices import AppServices
from src.event_management.event_messenger import EventMessenger
from src.event_management.events import Event
from src.server.app import FlaskServices
from src.server.config.repository.config_repository import ConfigRepositoryImpl
from src.server.config.serivce.ConfigLoadServiceFactory import ConfigLoadServiceFactory
from src.server.config.serivce.ConfigSaverServiceFactory import ConfigSaverServiceFactory
from src.server.config.serivce.config_load_service_impl import ConfigLoadServiceImpl
from src.server.config.serivce.config_saver_service_impl import ConfigSaverServiceImpl
from src.server.hot_key.repository.hot_key_repository import HotKeyRepositoryImpl
from src.server.hot_key.service.HotKeyServiceFactory import HotKeyServiceFactory
from src.server.hot_key.service.hot_key_service import HotKeyServiceImpl
from src.server.models.repository.model_repository import ModelRepositoryImpl
from src.server.models.service.LocalModelServiceFactory import LocalModelServiceFactory
from src.server.models.service.local_model_service import LocalModelServiceImpl
from src.runtime.transcription_runtime_manager import AudioTranscriptionRuntimeManager
from src.server.app import create_flask_app_with


def bootstrap() -> None:
    project_root = Path(__file__).resolve().parent
    src_path = project_root / "src"

    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    hot_key_service = HotKeyServiceFactory.get_hot_key_service()
    model_service = LocalModelServiceFactory.get_local_model_service()

    config_loader = ConfigLoadServiceFactory.get_config_loader()
    config_saver = ConfigSaverServiceFactory.get_config_saver()

    app_services = AppServices(project_root, config_loader, hot_key_service)

    audio_transcription_runtime = AudioTranscriptionRuntimeManager(app_services)
    # enure runtime is reloaded on config change though event subscription
    messenger = EventMessenger.get_instance()
    messenger.subscribe(Event.CONFIG_SAVED, audio_transcription_runtime.reload)
    audio_transcription_runtime.start()

    flask_app = create_flask_app_with(
        FlaskServices(
            model_service,
            hot_key_service,
            config_loader,
            config_saver,
        )
    )
    flask_app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    bootstrap()

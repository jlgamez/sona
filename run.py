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
from src.server.config.serivce.config_load_service_impl import ConfigLoadServiceImpl
from src.server.config.serivce.config_saver_service_impl import ConfigSaverServiceImpl
from src.server.hot_key.repository.hot_key_repository import HotKeyRepositoryImpl
from src.server.hot_key.service.hot_key_service import HotKeyServiceImpl
from src.server.models.repository.model_repository import ModelRepositoryImpl
from src.server.models.service.local_model_service import LocalModelServiceImpl
from src.runtime.runtime_manager import AudioTranscriptionRuntimeManager
from src.server.app import create_flask_app_with


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
    config_repository = ConfigRepositoryImpl()
    config_loader = ConfigLoadServiceImpl(config_repository, config_defaults)
    config_saver = ConfigSaverServiceImpl(config_repository)

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

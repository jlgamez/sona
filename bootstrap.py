#!/usr/bin/env python3
"""
Entry point for the Sona Audio Recorder CLI.
Ensures the project root is in sys.path and launches the main application logic.
"""
import sys
from pathlib import Path

from src.AppServices import AppServices
from src.event_management.Event import Event
from src.event_management.EventMessenger import EventMessenger
from src.runtime.AudioTranscriptionRuntimeManager import AudioTranscriptionRuntimeManager
from src.server.app import FlaskServices
from src.server.app import create_flask_app_with
from src.server.config.serivce.ConfigLoadServiceFactory import ConfigLoadServiceFactory
from src.server.config.serivce.ConfigSaverServiceFactory import ConfigSaverServiceFactory
from src.server.hot_key.service.HotKeyServiceFactory import HotKeyServiceFactory
from src.server.models.service.LocalModelServiceFactory import LocalModelServiceFactory


def get_project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def bootstrap() -> None:
    project_root = get_project_root()
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
    flask_app.run(debug=False, use_reloader=False)

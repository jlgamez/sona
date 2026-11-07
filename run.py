#!/usr/bin/env python3
"""
Entry point for the Sona Audio Recorder CLI.
Ensures the project root is in sys.path and launches the main application logic.
"""
import multiprocessing
import sys
from pathlib import Path

from src.AppServices import AppServices
from src.event_management.EventMessenger import EventMessenger
from src.event_management.Event import Event
from src.server.app import FlaskServices
from src.server.server_settings import ServerSettings
from src.utils.MacPermissions import MacPermissionsImpl
from src.utils.ParentWatcher import ParentWatcher
from src.server.config.repository.ConfigRepository import ConfigRepositoryImpl
from src.server.config.serivce.ConfigLoadServiceFactory import ConfigLoadServiceFactory
from src.server.config.serivce.ConfigSaverServiceFactory import ConfigSaverServiceFactory
from src.server.config.serivce.ConfigLoadServiceImpl import ConfigLoadServiceImpl
from src.server.config.serivce.ConfigSaverServiceImpl import ConfigSaverServiceImpl
from src.server.hot_key.repository.HotKeyRepository import HotKeyRepositoryImpl
from src.server.hot_key.service.HotKeyServiceFactory import HotKeyServiceFactory
from src.server.hot_key.service.HotKeyService import HotKeyServiceImpl
from src.server.models.repository.ModelRepository import ModelRepositoryImpl
from src.server.models.service.LocalModelServiceFactory import LocalModelServiceFactory
from src.server.models.service.LocalModelService import LocalModelServiceImpl
from src.runtime.AudioTranscriptionRuntimeManager import AudioTranscriptionRuntimeManager
from src.server.app import create_flask_app_with


def bootstrap() -> None:
    settings = ServerSettings.from_args(sys.argv[1:])
    if settings.exit_when_parent_dies:
        ParentWatcher().start()
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
            app_services.list_audio_devices,
            MacPermissionsImpl(),
        ),
        settings.allowed_origins,
    )
    print(f"Sona API listening on http://{settings.host}:{settings.port}")
    flask_app.run(
        host=settings.host, port=settings.port, debug=False, use_reloader=False
    )


if __name__ == "__main__":
    # Required in the PyInstaller build: libraries start helper processes from
    # this executable, and without this each one would run bootstrap() again.
    multiprocessing.freeze_support()
    bootstrap()

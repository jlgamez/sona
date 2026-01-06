"""
Download a Whisper model by name using Whisper's load_model.
This function only ensures the model is present in the local cache.
"""

from src.event_management.event_messenger import EventMessenger
from src.event_management.events import Event
from src.runtime.shared_executor import get_shared_executor


def download_whisper_model(model_name: str) -> None:
    try:
        import whisper

        whisper.load_model(model_name, device="cpu")
        EventMessenger.get_instance().emit(Event.MODEL_DOWNLOAD_COMPLETE, model_name)
    except Exception as exc:
        raise RuntimeError(f"Failed to download Whisper model '{model_name}'") from exc


def download_model_async(model_name: str) -> None:
    get_shared_executor().submit(download_whisper_model, model_name)

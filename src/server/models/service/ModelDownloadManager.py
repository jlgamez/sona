from threading import Lock
from typing import Set

from src.event_management.Event import Event
from src.event_management.EventMessenger import EventMessenger


class ModelDownloadManager:
    """Track which Whisper models are currently downloading.

    Responsibility:
        Keep a thread-safe set of model names with an in-progress download.
        Subscribes to ``Event.MODEL_DOWNLOAD_COMPLETE`` on creation so entries
        are removed when a download ends (successfully or not).

    Interface:
        * track_model_download(model_name) -> None
        * is_downloading(model_name) -> bool
    """

    def __init__(self) -> None:
        self._download_lock = Lock()
        self._active_downloads: Set[str] = set()
        EventMessenger.get_instance().subscribe(
            Event.MODEL_DOWNLOAD_COMPLETE, self._on_download_complete
        )

    def track_model_download(self, model_name: str) -> None:
        with self._download_lock:
            self._active_downloads.add(model_name)

    def is_downloading(self, model_name: str) -> bool:
        """Check if a model is currently downloading."""
        with self._download_lock:
            return model_name in self._active_downloads

    def _on_download_complete(self, model_name: str) -> None:
        """Event handler: stop tracking the model once its download ended."""
        with self._download_lock:
            self._active_downloads.discard(model_name)

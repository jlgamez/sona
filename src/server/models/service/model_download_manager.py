from threading import Lock


class ModelDownloadManager:
    _download_lock = Lock()
    _active_downloads: set[str] = set()
    _subscribed = False

    def track_model_download(self, model_name: str):
        with self._download_lock:
            if not self._subscribed:
                self._subscribe_to_download_complete_event()
                self._subscribed = True

            self._active_downloads.add(model_name)

    def is_downloading(self, model_name: str) -> bool:
        """Check if a model is currently downloading."""
        if not self._subscribed:
            raise Exception("Model download manager not subscribed to events")
        with self._download_lock:
            return model_name in self._active_downloads

    def _subscribe_to_download_complete_event(self):
        from src.event_management.event_messenger import EventMessenger
        from src.event_management.events import Event

        EventMessenger.get_instance().subscribe(
            Event.MODEL_DOWNLOAD_COMPLETE, self._on_download_complete
        )

    def _on_download_complete(self, model_name: str):
        """Event handler - reads model_name from temp storage"""
        with self._download_lock:
            self._active_downloads.discard(model_name)

from src.core.transcription.device.DeviceCleanupService import (
    DeviceCleanupServiceImpl,
)
from src.core.transcription.device.DeviceSelector import DeviceSelectorImpl


class DeviceManager:
    def __init__(self):
        self._device_selector = DeviceSelectorImpl()
        self.device_cleanup_service = DeviceCleanupServiceImpl()

    def get_platform_device(self):
        return self._device_selector.select_device()

    def clear_device_cache(self):
        self.device_cleanup_service.clear_cache(self.get_platform_device())

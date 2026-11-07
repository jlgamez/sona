import ctypes
import sys
from typing import Literal, Protocol

PermissionState = Literal["granted", "denied", "unknown"]

_IOKIT_PATH = "/System/Library/Frameworks/IOKit.framework/IOKit"
_APP_SERVICES_PATH = (
    "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
)
# IOHIDRequestType: 0 is PostEvent, 1 is ListenEvent (Input Monitoring).
_REQUEST_TYPE_LISTEN_EVENT = 1
# IOHIDAccessType values returned by IOHIDCheckAccess.
_ACCESS_GRANTED = 0
_ACCESS_DENIED = 1


class PermissionChecker(Protocol):
    """Responsibility: report and request the macOS privacy grants Sona needs.

    Interface: ``input_monitoring()``, ``accessibility()`` and
    ``request_input_monitoring()``. Checks describe the grants of this process
    (the app that launched it), which are the ones the hotkey listener and the
    paste keystroke use.
    """

    def input_monitoring(self) -> PermissionState: ...

    def accessibility(self) -> PermissionState: ...

    def request_input_monitoring(self) -> None: ...


class MacPermissionsImpl(PermissionChecker):
    """Responsibility: read macOS privacy grants through ctypes, no extra packages.

    Interface: see ``PermissionChecker``. Never raises: off macOS, or when a
    system call is unavailable, the state is ``"unknown"``.
    """

    def input_monitoring(self) -> PermissionState:
        iokit = self._load(_IOKIT_PATH)
        if iokit is None:
            return "unknown"
        try:
            iokit.IOHIDCheckAccess.argtypes = [ctypes.c_uint32]
            iokit.IOHIDCheckAccess.restype = ctypes.c_uint32
            result = iokit.IOHIDCheckAccess(_REQUEST_TYPE_LISTEN_EVENT)
        except (AttributeError, OSError):
            return "unknown"
        if result == _ACCESS_GRANTED:
            return "granted"
        if result == _ACCESS_DENIED:
            return "denied"
        return "unknown"

    def accessibility(self) -> PermissionState:
        services = self._load(_APP_SERVICES_PATH)
        if services is None:
            return "unknown"
        try:
            services.AXIsProcessTrusted.restype = ctypes.c_bool
            trusted = services.AXIsProcessTrusted()
        except (AttributeError, OSError):
            return "unknown"
        return "granted" if trusted else "denied"

    def request_input_monitoring(self) -> None:
        iokit = self._load(_IOKIT_PATH)
        if iokit is None:
            return
        try:
            iokit.IOHIDRequestAccess.argtypes = [ctypes.c_uint32]
            iokit.IOHIDRequestAccess.restype = ctypes.c_bool
            iokit.IOHIDRequestAccess(_REQUEST_TYPE_LISTEN_EVENT)
        except (AttributeError, OSError):
            return

    @staticmethod
    def _load(path: str) -> ctypes.CDLL | None:
        if sys.platform != "darwin":
            return None
        try:
            return ctypes.CDLL(path)
        except OSError:
            return None

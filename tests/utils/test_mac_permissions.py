import sys

from src.utils import MacPermissions
from src.utils.MacPermissions import MacPermissionsImpl


def test_unknown_off_macos(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    permissions = MacPermissionsImpl()
    assert permissions.input_monitoring() == "unknown"
    assert permissions.accessibility() == "unknown"
    permissions.request_input_monitoring()


def test_input_monitoring_maps_access_codes(monkeypatch):
    class FakeFn:
        def __init__(self, code):
            self.code = code

        def __call__(self, request_type):
            return self.code

    for code, expected in [(0, "granted"), (1, "denied"), (2, "unknown")]:
        lib = type("Lib", (), {"IOHIDCheckAccess": FakeFn(code)})()
        monkeypatch.setattr(sys, "platform", "darwin")
        monkeypatch.setattr(MacPermissions.ctypes, "CDLL", lambda path, lib=lib: lib)
        assert MacPermissionsImpl().input_monitoring() == expected

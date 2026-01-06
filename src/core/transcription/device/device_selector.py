from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class DeviceSelector(Protocol):
    """DeviceSelector

    Responsibility:
        Decide the optimal inference device string ("mps", "cuda", or "cpu")
        and report fp16 capability for that device. Keeps hardware probing
        isolated from transcription logic.

    Interface:
        * select_device() -> str
        * supports_fp16(device: str) -> bool
    """

    def select_device(self) -> str:
        """Return the selected device string."""

    def supports_fp16(self, device: str) -> bool:
        """Return True if fp16 is usable on the given device."""


class DeviceSelectorImpl(DeviceSelector):
    """DefaultDeviceSelector

    Responsibility:
        Provide a concrete, platform-aware device selection strategy for
        Whisper inference. Probes Torch backends lazily to decide between
        "mps", "cuda", and "cpu", and reports fp16 support for the chosen
        device.

    Interface:
        * select_device() -> str: Prefer MPS on Apple Silicon, then CUDA, else CPU.
        * supports_fp16(device: str) -> bool: Indicates whether half-precision is
          advisable for the given device.
    """

    def _is_mps_available(self) -> bool:
        """Check if MPS backend is available in torch."""
        try:
            import torch
            return getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
        except Exception:
            return False

    def select_device(self) -> str:
        """Select the best available device.
        Decision order (lazy):
        1. MPS if torch with MPS backend is available.
        2. CUDA if torch with CUDA is available.
        3. CPU as fallback.
        """
        try:
            import torch  # Lazy import to avoid startup latency
        except Exception:
            return "cpu"

        # Prefer Apple Silicon MPS when available.
        if self._is_mps_available():
            return "mps"

        # Next prefer CUDA on NVIDIA GPUs.
        try:
            if torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass

        # Fallback to CPU.
        return "cpu"

    def supports_fp16(self, device: str) -> bool:
        """Return True if using fp16 is likely beneficial and supported.
        """
        if device == "cpu":
            return False

        if device == "mps":
            return self._is_mps_available()

        if device == "cuda":
            try:
                import torch
                if not torch.cuda.is_available():
                    return False
                # Optional: check device capability; most modern GPUs support fp16.
                try:
                    major, minor = torch.cuda.get_device_capability(0)
                    # Enable fp16 for compute capability >= 5.3 (Maxwell and newer).
                    return (major, minor) >= (5, 3)
                except Exception:
                    # If capability probing fails, default to True when CUDA is available.
                    return True
            except Exception:
                return False

        # Unknown device strings: be conservative.
        return False


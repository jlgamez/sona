"""Device cleanup service for releasing GPU/device memory caches."""

from __future__ import annotations

from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class DeviceCleanupService(Protocol):
    """Protocol for clearing device-specific memory caches."""

    def clear_cache(self, device: Optional[str] = None) -> None:
        """Clear the cache for the specified device (cuda, mps, or both if None)."""
        ...


class DeviceCleanupServiceImpl(DeviceCleanupService):
    """Best-effort clearing of CUDA and MPS device caches."""

    def clear_cache(self, device: Optional[str] = None) -> None:
        """Clear the cache for the specified device."""
        try:
            import torch  # type: ignore
        except Exception:
            return

        dev = (device or "").lower()

        if self._should_clear_cuda_cache(dev, torch):
            self._clear_cuda_cache(torch)

        if self._should_clear_mps_cache(dev, torch):
            self._clear_mps_cache(torch)

    @staticmethod
    def _should_clear_cuda_cache(dev: str, torch: Any) -> bool:
        """Check if CUDA cache should be cleared."""
        if "cuda" not in dev and dev:
            return False
        cuda = getattr(torch, "cuda", None)
        return cuda is not None and cuda.is_available()

    @staticmethod
    def _clear_cuda_cache(torch: Any) -> None:
        """Attempt to clear CUDA cache."""
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass

    @staticmethod
    def _should_clear_mps_cache(dev: str, torch: Any) -> bool:
        """Check if MPS cache should be cleared."""
        if "mps" not in dev and dev:
            return False
        mps_backend = getattr(getattr(torch, "backends", None), "mps", None)
        return mps_backend is not None and mps_backend.is_available()

    @staticmethod
    def _clear_mps_cache(torch: Any) -> None:
        """Attempt to clear MPS cache (Apple Silicon)."""
        try:
            mps_module = getattr(torch, "mps", None)
            if mps_module is not None and hasattr(mps_module, "empty_cache"):
                mps_module.empty_cache()
        except Exception:
            pass

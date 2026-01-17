from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class CleanupService(Protocol):
    """CleanupService

    Responsibility:
        Best-effort cleanup for temporary files. Must be idempotent and
        resilient to IO errors.

    Interface:
        * delete_file(path: Path) -> None
    """

    def delete_file(self, path: Path) -> None:
        """Remove the temp audio file if it exists (idempotent)."""



class CleanupServiceImpl(CleanupService):
    """CleanupServiceImpl

    Responsibility:
        Concrete implementation that performs best-effort cleanup for temporary
        files. Resilient to IO errors and fully idempotent—safe to call multiple
        times on the same resource.

    Interface:
        * delete_file(path: Path) -> None
    """

    def delete_file(self, path: Path) -> None:
        """Remove the temp audio file if it exists (idempotent).

        Args:
            path: Path to the temporary audio file to delete
        """
        try:
            if path.exists() and path.is_file():
                path.unlink()
                print(f"[DEBUG] Deleted temporary file: {path}")
        except FileNotFoundError:
            # Already deleted or never existed - idempotent behavior
            pass
        except PermissionError as e:
            print(f"[WARNING] Permission denied deleting file {path}: {e}")
        except OSError as e:
            print(f"[WARNING] Failed to delete file {path}: {e}")


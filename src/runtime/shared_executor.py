# python
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Optional
import atexit

_lock = Lock()
_executor: Optional[ThreadPoolExecutor] = None


DEFAULT_MAX_WORKERS = 3


def get_shared_executor() -> ThreadPoolExecutor:
    """Return a singleton ThreadPoolExecutor for the process."""
    global _executor
    with _lock:
        if _executor is None:
            _executor = ThreadPoolExecutor(
                max_workers=DEFAULT_MAX_WORKERS, thread_name_prefix="shared-worker"
            )
        return _executor


def shutdown_shared_executor(wait: bool = True) -> None:
    """Shutdown the shared executor (registered with atexit)."""
    global _executor
    with _lock:
        if _executor is not None:
            _executor.shutdown(wait=wait, cancel_futures=not wait)
            _executor = None


# Ensure cleanup at process exit
atexit.register(shutdown_shared_executor)

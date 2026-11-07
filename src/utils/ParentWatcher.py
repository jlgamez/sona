import os
import signal
import sys
import threading


class ParentWatcher:
    """Responsibility: stop this process when the process that started it is gone.

    Interface: ``start()``. The parent keeps this process's stdin open as a pipe;
    when the parent exits or crashes the OS closes the pipe and stdin reaches EOF.
    The watcher then sends SIGTERM to itself, which takes the same shutdown path
    as a normal stop, so no recording process is left behind.
    """

    def start(self) -> None:
        threading.Thread(target=self._wait_for_parent_exit, daemon=True).start()

    def _wait_for_parent_exit(self) -> None:
        try:
            sys.stdin.read()
        except (OSError, ValueError):
            pass
        print("[INFO] Parent process is gone; shutting down.")
        os.kill(os.getpid(), signal.SIGTERM)

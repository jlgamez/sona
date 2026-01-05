from collections import defaultdict
from typing import Callable


class EventBus:
    def __init__(self):
        self._handlers = defaultdict(list)

    def subscribe(self, event_name: str, handler: Callable):
        self._handlers[event_name].append(handler)

    def emit(self, event_name: str):
        for handler in self._handlers[event_name]:
            handler()

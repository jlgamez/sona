from collections import defaultdict
from typing import Callable, Optional, DefaultDict, List

from src.event_management.events import Event


class EventMessenger:
    _instance: Optional[EventMessenger] = None

    def __init__(self):
        self._handlers: DefaultDict[Event, List[Callable]] = defaultdict(list)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EventMessenger()
        return cls._instance

    def subscribe(self, event: Event, handler: Callable):
        self._handlers[event].append(handler)

    def emit(self, event: Event):
        for handler in self._handlers[event]:
            try:
                handler()
            except Exception as e:
                print(f"[EventMessenger] Error in event {event.name} handler: {e}")

"""
core/event_bus.py
Simple publish/subscribe event bus.
Allows decoupled communication between systems.
Subscribe events can be used later for UI animations, analytics, multiplayer sync.
"""
from collections import defaultdict


class EventBus:
    def __init__(self):
        self._handlers: dict[str, list] = defaultdict(list)

    def subscribe(self, event_name: str, fn):
        """Register a handler for the given event."""
        self._handlers[event_name].append(fn)

    def emit(self, event_name: str, **kwargs):
        """Fire all handlers registered for event_name."""
        for fn in self._handlers[event_name]:
            fn(**kwargs)

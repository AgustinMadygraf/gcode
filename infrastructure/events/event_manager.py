"""
infrastructure/events/event_manager.py
Gestor de eventos desacoplado de la UI (Observer pattern).
"""

from collections import defaultdict

class EventManager:
    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self._subscribers[event_type].append(handler)

    def publish(self, event):
        for handler in self._subscribers[type(event)]:
            handler(event)

"""
EventBus desacoplado y tipado para la aplicación.
"""
from typing import Callable, Dict, List, Type, Any
from domain.events.events import Event

class EventBus:
    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event: Event):
        for handler in self._subscribers.get(type(event), []):
            handler(event)

# Implementación simple de EventBusPort
from domain.ports.event_bus_port import EventBusPort
from typing import Callable, Any, Dict, List

class SimpleEventBus(EventBusPort):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def publish(self, event_type: str, payload: Any) -> None:
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            handler(payload)

    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

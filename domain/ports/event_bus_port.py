# Puerto para bus de eventos (EventBus)
from abc import ABC, abstractmethod
from typing import Callable, Any

class EventBusPort(ABC):
    @abstractmethod
    def publish(self, event_type: str, payload: Any) -> None:
        """Publica un evento de un tipo específico con un payload."""
        pass

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Suscribe un handler a un tipo de evento."""
        pass

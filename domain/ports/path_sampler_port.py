from abc import ABC, abstractmethod
from typing import Iterable
from domain.models import Point

class IPathSampler(ABC):
    @abstractmethod
    def sample(self, path) -> Iterable[Point]:
        """Genera puntos a lo largo de un path."""
        pass

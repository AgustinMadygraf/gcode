"""
Path: domain/ports/path_sampler_port.py
"""

from abc import ABC, abstractmethod
from typing import Iterable
from domain.models import Point

class IPathSampler(ABC):
    " Interfaz para muestreo de puntos a lo largo de rutas SVG. "
    @abstractmethod
    def sample(self, path) -> Iterable[Point]:
        """Genera puntos a lo largo de un path."""
        pass

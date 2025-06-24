"""
Puerto PathSamplerPort: interfaz para muestreo de puntos en rutas SVG en el dominio.
"""

from abc import ABC, abstractmethod
from typing import Iterable
from domain.entities.point import Point

class PathSamplerPort(ABC):
    """
    Interfaz para muestrear puntos a lo largo de un path SVG.
    """
    @abstractmethod
    def sample(self, path) -> Iterable[Point]:
        """Genera puntos a lo largo de un path."""
        pass

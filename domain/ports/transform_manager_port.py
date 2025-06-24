"""
Puerto para la gestión de transformaciones de puntos en el dominio.
Define la interfaz TransformManagerPort para aplicar estrategias de transformación.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from domain.path_transform_strategy import PathTransformStrategy

class TransformManagerPort(ABC):
    @abstractmethod
    def apply(self, x: float, y: float) -> Tuple[float, float]:
        """Aplica todas las estrategias de transformación al punto (x, y)."""
        pass

    @abstractmethod
    def add_strategy(self, strategy: PathTransformStrategy):
        """Agrega una nueva estrategia de transformación."""
        pass

class NullTransformManager:
    def apply(self, x, y):
        return x, y

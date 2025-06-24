"""
Puerto: PathTransformStrategyPort
Interfaz para estrategias de transformación de paths SVG.
"""
from abc import ABC, abstractmethod

class PathTransformStrategyPort(ABC):
    @abstractmethod
    def transform(self, x: float, y: float) -> tuple[float, float]:
        """
        Transforma un punto (x, y) y retorna el nuevo punto transformado.
        """
        pass

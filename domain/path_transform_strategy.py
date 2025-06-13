"""
PathTransformStrategy: Interfaz para estrategias de transformación de paths SVG.
"""
from abc import ABC, abstractmethod

class PathTransformStrategy(ABC):
    "Interfaz para estrategias de transformación de paths SVG."
    @abstractmethod
    def transform(self, x: float, y: float) -> tuple[float, float]:
        """
        Transforma un punto (x, y) y retorna el nuevo punto transformado.
        """
        pass

class Rotate180Strategy(PathTransformStrategy):
    " Estrategia para rotar un punto 180 grados alrededor del origen. "
    def __init__(self, cx: float, cy: float):
        self.cx = cx
        self.cy = cy

    def transform(self, x: float, y: float) -> tuple[float, float]:
        x2 = 2 * self.cx - x
        y2 = 2 * self.cy - y
        return x2, y2

class MirrorHorizontalStrategy(PathTransformStrategy):
    "Estrategia para reflejar un punto horizontalmente."
    def __init__(self, cx: float):
        self.cx = cx

    def transform(self, x: float, y: float) -> tuple[float, float]:
        return 2 * self.cx - x, y

class MirrorVerticalStrategy(PathTransformStrategy):
    "Estrategia para reflejar un punto verticalmente."
    def __init__(self, cy: float):
        self.cy = cy

    def transform(self, x: float, y: float) -> tuple[float, float]:
        return x, 2 * self.cy - y

class ScaleStrategy(PathTransformStrategy):
    "Estrategia para escalar un punto."
    def __init__(self, scale: float):
        self.scale = scale

    def transform(self, x: float, y: float) -> tuple[float, float]:
        return x * self.scale, y * self.scale

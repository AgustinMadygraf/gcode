"""
Implementaciones concretas de PathTransformStrategyPort.
"""
from domain.ports.path_transform_strategy_port import PathTransformStrategyPort

class VerticalFlipStrategy(PathTransformStrategyPort):
    "Estrategia para aplicar flip vertical respecto a una línea horizontal y = cy."
    def __init__(self, cy: float):
        self.cy = cy

    def transform(self, x: float, y: float) -> tuple[float, float]:
        result = (x, self.cy - (y - self.cy))
        return result

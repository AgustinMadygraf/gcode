"""
Implementaciones concretas de PathTransformStrategyPort.
"""
from domain.ports.path_transform_strategy_port import PathTransformStrategyPort

class MirrorVerticalStrategy(PathTransformStrategyPort):
    def __init__(self, cy: float):
        self.cy = cy

    def transform(self, x: float, y: float) -> tuple[float, float]:
        return x, 2 * self.cy - y

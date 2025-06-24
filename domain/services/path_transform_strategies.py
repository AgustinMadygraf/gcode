"""
Implementaciones concretas de PathTransformStrategyPort.
"""
from domain.ports.path_transform_strategy_port import PathTransformStrategyPort

class Rotate180Strategy(PathTransformStrategyPort):
    def __init__(self, cx: float, cy: float):
        self.cx = cx
        self.cy = cy

    def transform(self, x: float, y: float) -> tuple[float, float]:
        x2 = 2 * self.cx - x
        y2 = 2 * self.cy - y
        return x2, y2

class MirrorHorizontalStrategy(PathTransformStrategyPort):
    def __init__(self, cx: float):
        self.cx = cx

    def transform(self, x: float, y: float) -> tuple[float, float]:
        return 2 * self.cx - x, y

class MirrorVerticalStrategy(PathTransformStrategyPort):
    def __init__(self, cy: float):
        self.cy = cy

    def transform(self, x: float, y: float) -> tuple[float, float]:
        return x, 2 * self.cy - y

"""
TransformManager: Aplica una secuencia de estrategias de transformación a puntos (x, y).

- Permite agregar estrategias (callables) que reciben y devuelven (x, y).
- El método apply(x, y) aplica todas las estrategias en orden.

Ejemplo de uso:
    def mirror_x(x, y):
        return -x, y
    tm = TransformManager([mirror_x])
    x2, y2 = tm.apply(1, 2)  # (-1, 2)
"""
from typing import List, Tuple, Callable

class TransformManager:
    """Manages and applies a list of transformation strategies to (x, y) points."""
    def __init__(self, strategies: List[Callable[[float, float], Tuple[float, float]]] = None):
        self.strategies = strategies or []

    def add_strategy(self, strategy: Callable[[float, float], Tuple[float, float]]):
        " Adds a new transformation strategy to the manager. "
        self.strategies.append(strategy)

    def apply(self, x: float, y: float) -> Tuple[float, float]:
        " Applies all transformation strategies to the given (x, y) coordinates. "
        for strategy in self.strategies:
            x, y = strategy(x, y)
        return x, y

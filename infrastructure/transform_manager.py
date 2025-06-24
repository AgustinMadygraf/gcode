"""
TransformManager: Aplica una secuencia de estrategias de transformación a puntos (x, y).

- Permite agregar estrategias (callables) que reciben y devuelven (x, y).
- El método apply(x, y) aplica todas las estrategias en orden.

Args:
    strategies: Lista de funciones/callables que reciben (x: float, y: float) y devuelven (x, y).

Methods:
    add_strategy(strategy): Agrega una estrategia de transformación.
    apply(x, y): Aplica todas las estrategias en orden y retorna el resultado.

Ejemplo de uso:
    def mirror_x(x, y):
        return -x, y
    tm = TransformManager([mirror_x])
    x2, y2 = tm.apply(1, 2)  # (-1, 2)
"""
from domain.path_transform_strategy import PathTransformStrategy
from domain.ports.logger_port import LoggerPort
from infrastructure.exceptions import TransformStrategyError

class TransformManager:
    """Gestiona y aplica una lista de estrategias de transformación a puntos (x, y).
    Todas las estrategias deben implementar PathTransformStrategy.
    """
    def __init__(self, strategies: list[PathTransformStrategy] = None, logger: LoggerPort = None):
        if strategies is not None:
            for s in strategies:
                if not isinstance(s, PathTransformStrategy):
                    raise TransformStrategyError("Todas las estrategias deben implementar PathTransformStrategy")
        self.strategies = strategies or []
        self.logger: LoggerPort = logger

    def add_strategy(self, strategy: PathTransformStrategy):
        """Agrega una nueva estrategia de transformación al manager."""
        if not isinstance(strategy, PathTransformStrategy):
            raise TransformStrategyError("La estrategia debe implementar PathTransformStrategy")
        self.strategies.append(strategy)

    def apply(self, x: float, y: float) -> tuple[float, float]:
        """Aplica todas las estrategias de transformación al punto (x, y)."""
        for strategy in self.strategies:
            x, y = strategy.transform(x, y)
#            if self.logger:
#                msg = "Transform applied: {} -> ({:.3f}, {:.3f})"
#                self.logger.debug(msg.format(strategy.__class__.__name__, x, y))
        return x, y

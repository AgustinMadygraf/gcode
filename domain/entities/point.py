"""
Entidad Point: representa un punto 2D en el dominio.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    """Representa un punto en el espacio 2D."""
    x: float
    y: float

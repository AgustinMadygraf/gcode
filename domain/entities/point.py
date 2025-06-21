"""
Entidad Point: representa un punto 2D en el dominio.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

"""
Entidad Segment: representa un segmento entre dos puntos.
"""
from dataclasses import dataclass
from domain.entities.point import Point

@dataclass(frozen=True)
class Segment:
    " Representa un segmento entre dos puntos en el espacio 2D. "
    start: Point
    end: Point

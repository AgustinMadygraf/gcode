"""
geometry_rotate.py: Función utilitaria para rotar puntos y paths 90° en sentido horario respecto al origen.
"""
from domain.entities.point import Point
from domain.entities.segment import Segment
from domain.entities.path import Path as DomainPath

def rotate_point_90_clockwise(point: Point) -> Point:
    """Rota un punto 90° horario respecto al origen (x, y) -> (y, -x)."""
    return Point(x=point.y, y=-point.x)

def rotate_segment_90_clockwise(segment: Segment) -> Segment:
    " Rota un segmento 90° horario respecto al origen. "
    return Segment(
        start=rotate_point_90_clockwise(segment.start),
        end=rotate_point_90_clockwise(segment.end)
    )

def rotate_path_90_clockwise(path: DomainPath) -> DomainPath:
    " Rota un path 90° horario respecto al origen. "
    return DomainPath(segments=[rotate_segment_90_clockwise(seg) for seg in path.segments])

def rotate_paths_90_clockwise(paths: list[DomainPath]) -> list[DomainPath]:
    " Rota una lista de paths 90° horario respecto al origen. """
    return [rotate_path_90_clockwise(p) for p in paths]

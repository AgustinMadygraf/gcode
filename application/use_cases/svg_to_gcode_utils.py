"""
Utilidades para conversión de svgpathtools.Path a entidades de dominio (Path, Segment, Point).
"""

from svgpathtools import Path as SvgPath
from domain.entities.path import Path as DomainPath
from domain.entities.segment import Segment
from domain.entities.point import Point


def svgpathtools_path_to_domain_path(svg_path: SvgPath) -> DomainPath:
    """Convierte un svgpathtools.Path a una entidad de dominio Path."""
    segments = []
    for seg in svg_path:
        # Soporta Line, CubicBezier, QuadraticBezier, Arc
        start = seg.start
        end = seg.end
        segments.append(Segment(
            start=Point(x=start.real, y=start.imag),
            end=Point(x=end.real, y=end.imag)
        ))
    return DomainPath(segments=segments)

def svgpathtools_paths_to_domain_paths(paths):
    """Convierte una lista de svgpathtools.Path a lista de DomainPath."""
    return [svgpathtools_path_to_domain_path(p) for p in paths]

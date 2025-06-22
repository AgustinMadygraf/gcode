"""
Path: domain/path_filter.py
PathFilter: Encapsula la lógica de filtrado de paths SVG según criterios configurables.
Permite inyectar estrategias de filtrado adicionales.
"""
from typing import List, Any, Callable
from domain.filters.svg_border_detector import SvgBorderDetector

class PathFilter:
    " Encapsula la lógica de filtrado de paths SVG según criterios configurables. "
    def __init__(self, min_length: float = 1e-3, extra_filters: List[Callable[[Any], bool]] = None,
                 remove_svg_border: bool = True, border_tolerance: float = 0.05):
        self.min_length = min_length
        self.extra_filters = extra_filters or []
        self.remove_svg_border = remove_svg_border
        self.border_detector = SvgBorderDetector(tolerance=border_tolerance) if remove_svg_border else None

    def filter_nontrivial(self, paths: List[Any], svg_attr: dict = None) -> List[Any]:
        """
        Filtra paths que sean solo un punto, tengan longitud despreciable,
        o representen el borde del SVG (si remove_svg_border=True).
        Args:
            paths: Lista de paths SVG (cada uno iterable de segmentos con .length()).
            svg_attr: Atributos SVG para detectar el borde (opcional si remove_svg_border=False).
        Returns:
            Lista de paths útiles.
        """
        filtered = []
        for _i, p in enumerate(paths):
            total_length = sum(seg.length() for seg in p)
            if total_length <= self.min_length:
                continue
            if not all(f(p) for f in self.extra_filters):
                continue
            if self.remove_svg_border and svg_attr and self.border_detector.matches_svg_bounds(p, svg_attr):
                continue
            filtered.append(p)
        return filtered

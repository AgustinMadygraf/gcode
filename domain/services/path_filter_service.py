"""
Implementación concreta de PathFilterPort para filtrado de paths SVG.
"""
from typing import List, Any, Callable
from domain.ports.path_filter_port import PathFilterPort
from domain.filters.svg_border_detector import SvgBorderDetector

class PathFilter(PathFilterPort):
    def __init__(self, min_length: float = 1e-3, extra_filters: List[Callable[[Any], bool]] = None,
                 remove_svg_border: bool = True, border_tolerance: float = 0.05):
        self.min_length = min_length
        self.extra_filters = extra_filters or []
        self.remove_svg_border = remove_svg_border
        self.border_detector = SvgBorderDetector(tolerance=border_tolerance) if remove_svg_border else None

    def filter_nontrivial(self, paths: List[Any], svg_attr: dict = None) -> List[Any]:
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

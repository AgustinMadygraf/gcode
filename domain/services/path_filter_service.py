"""
Implementación concreta de PathFilterPort para filtrado de paths SVG.
"""
from typing import List, Any, Callable
from domain.ports.path_filter_port import PathFilterPort
from domain.filters.svg_border_detector import SvgBorderDetector

class PathFilter(PathFilterPort):
    def __init__(self, min_length: float = 1e-3, extra_filters: List[Callable[[Any], bool]] = None,
                 remove_svg_border: bool = True, border_tolerance: float = 0.05, logger=None):
        self.min_length = min_length
        self.extra_filters = extra_filters or []
        self.remove_svg_border = remove_svg_border
        if logger is None:
            raise RuntimeError("Logger debe ser inyectado en PathFilter. Usar siempre el constructor con logger explícito.")
        self.logger = logger
        self.border_detector = SvgBorderDetector(tolerance=border_tolerance, logger=logger) if remove_svg_border else None

    def filter_nontrivial(self, paths: List[Any], svg_attr: dict = None) -> List[Any]:
        filtered = []
        removed = 0
        for _i, p in enumerate(paths):
            total_length = sum(seg.length() for seg in p)
            if total_length <= self.min_length:
                self.logger.debug(f"Path {_i}: descartado por longitud ({total_length:.4f})")
                continue
            if not all(f(p) for f in self.extra_filters):
                self.logger.debug(f"Path {_i}: descartado por filtro extra")
                continue
            if self.remove_svg_border and svg_attr and self.border_detector.matches_svg_bounds(p, svg_attr):
                self.logger.info(f"Path {_i}: eliminado como borde SVG (rectángulo coincide con viewBox)")
                removed += 1
                continue
            filtered.append(p)
        self.logger.info(f"Total de paths eliminados como borde SVG: {removed}")
        return filtered

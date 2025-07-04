"""
Path: domain/services/path_filter_service.py
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
            msg = f"Path {_i}: longitud total={total_length:.4f}, segmentos={len(p)}"
            self.logger.debug(msg)
            if total_length <= self.min_length:
                msg = f"Path {_i}: descartado por longitud ({total_length:.4f})"
                self.logger.debug(msg)
                continue
            if not all(f(p) for f in self.extra_filters):
                msg = f"Path {_i}: descartado por filtro extra"
                self.logger.debug(msg)
                continue
            if self.remove_svg_border and svg_attr:
                msg = f"Path {_i}: evaluando como posible borde (segmentos={len(p)})"
                self.logger.debug(msg)
                borde = self.border_detector.matches_svg_bounds(p, svg_attr)
                msg = f"Path {_i}: matches_svg_bounds={borde}"
                self.logger.debug(msg)
                if borde:
                    msg = f"Path {_i}: eliminado como borde SVG (rectángulo coincide con viewBox)"
                    self.logger.info(msg)
                    removed += 1
                    continue
                else:
                    msg = f"Path {_i}: NO eliminado como borde SVG"
                    self.logger.debug(msg)
            filtered.append(p)
        msg = f"Total de paths eliminados como borde SVG: {removed}"
        self.logger.info(msg)
        return filtered

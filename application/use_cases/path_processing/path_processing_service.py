"""
Servicio de aplicación para procesar paths SVG: división en subpaths continuos,
filtrado y transformaciones.
(Movido desde domain/path_processing_service.py)
"""
from typing import List, Any, Callable
from svgpathtools import Path as SvgPath
from domain.services.path_filter_service import PathFilter

class PathProcessingService:
    """ Servicio de aplicación para procesar paths SVG: 
    división en subpaths continuos, filtrado y transformaciones. """
    def __init__(self,
                 min_length: float = 1e-3,
                 extra_filters: list[Callable[[Any], bool]] = None,
                 transform_strategies: list = None,
                 remove_svg_border: bool = True,
                 border_tolerance: float = 0.05):
        self.path_filter = PathFilter(min_length, extra_filters, remove_svg_border, border_tolerance)
        self.transform_strategies = transform_strategies or []

    def split_path_into_continuous_subpaths(self, path, tol=1e-6) -> List[SvgPath]:
        """
        Divide un path en subpaths continuos.
        Args:
            path: Un objeto Path de svgpathtools (o similar, iterable de segmentos).
            tol: Tolerancia para considerar dos puntos como conectados.
        Returns:
            Lista de subpaths (cada uno es un objeto Path de svgpathtools).
        """
        if not path:
            return []
        subpaths = []
        current = [path[0]]
        for seg_prev, seg_next in zip(path, path[1:]):
            if abs(seg_prev.point(1) - seg_next.point(0)) < tol:
                current.append(seg_next)
            else:
                subpaths.append(SvgPath(*current))
                current = [seg_next]
        if current:
            subpaths.append(SvgPath(*current))
        return subpaths

    def process(self, paths: list, attributes: dict) -> list:
        """
        Procesa los paths: divide en subpaths continuos y filtra los triviales.
        """
        # 1. Dividir paths discontinuos en subpaths continuos
        all_subpaths = []
        for p in paths:
            subpaths = self.split_path_into_continuous_subpaths(p)
            all_subpaths.extend(subpaths)
        # 2. Filtrar paths triviales y bordes SVG
        filtered = self.path_filter.filter_nontrivial(all_subpaths, attributes)
        # 3. (Transformaciones de puntos se aplican en GCodeGenerator, no aquí)
        return filtered

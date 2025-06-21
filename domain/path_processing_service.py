"""
Path: domain/path_processing_service.py
Servicio de dominio para procesar paths SVG: división en subpaths continuos,
filtrado y transformaciones.
"""
from typing import List, Any, Callable
from svgpathtools import Path as SvgPath
from domain.path_filter import PathFilter

class PathProcessingService:
    """ Servicio de dominio para procesar paths SVG: 
    división en subpaths continuos, filtrado y transformaciones. """
    def __init__(self,
                 min_length: float = 1e-3,
                 extra_filters: list[Callable[[Any], bool]] = None,
                 transform_strategies: list = None):
        self.path_filter = PathFilter(min_length, extra_filters)
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

    def process(self, paths: list, _attributes: dict) -> list:
        """
        Procesa los paths: divide en subpaths continuos y filtra los triviales.
        El argumento 'attributes' se acepta para compatibilidad futura.
        """
        # 1. Dividir paths discontinuos en subpaths continuos
        all_subpaths = []
        for p in paths:
            subpaths = self.split_path_into_continuous_subpaths(p)
            all_subpaths.extend(subpaths)
        # 2. Filtrar paths triviales
        filtered = self.path_filter.filter_nontrivial(all_subpaths)
        # 3. (Transformaciones de puntos se aplican en GCodeGenerator, no aquí)
        return filtered

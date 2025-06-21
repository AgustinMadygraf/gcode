"""
Path: domain/path_filter.py
PathFilter: Encapsula la lógica de filtrado de paths SVG según criterios configurables.
Permite inyectar estrategias de filtrado adicionales.
"""
from typing import List, Any, Callable

class PathFilter:
    " Encapsula la lógica de filtrado de paths SVG según criterios configurables. "
    def __init__(self, min_length: float = 1e-3, extra_filters: List[Callable[[Any], bool]] = None):
        self.min_length = min_length
        self.extra_filters = extra_filters or []

    def filter_nontrivial(self, paths: List[Any]) -> List[Any]:
        """
        Filtra paths que sean solo un punto o tengan longitud despreciable,
        y aplica filtros adicionales si se proporcionan.
        Args:
            paths: Lista de paths SVG (cada uno iterable de segmentos con .length()).
        Returns:
            Lista de paths útiles.
        """
        filtered = []
        for _i, p in enumerate(paths):
            total_length = sum(seg.length() for seg in p)
            if total_length > self.min_length and all(f(p) for f in self.extra_filters):
                filtered.append(p)
        return filtered

"""
TrajectoryOptimizer: Reordena paths/segmentos para minimizar movimientos en vacío (greedy).
"""
from typing import List

class TrajectoryOptimizer:
    def optimize_order(self, paths: List) -> List:
        """
        Reordena los paths para minimizar la distancia entre el final de uno y el inicio del siguiente.
        paths: lista de objetos con atributos start_point y end_point, o una lista de puntos.
        Omite paths vacíos o inválidos.
        """
        # Filtrar paths inválidos
        valid_paths = []
        for p in paths:
            try:
                # Verifica que tenga al menos un punto válido
                _ = self._get_start_point(p)
                _ = self._get_end_point(p)
                valid_paths.append(p)
            except AttributeError:
                print(f"[TrajectoryOptimizer][WARN] Path inválido omitido: {p}")
                continue
        if not valid_paths:
            return []
        ordered = []
        remaining = valid_paths[:]
        current = remaining.pop(0)
        ordered.append(current)
        while remaining:
            last_point = self._get_end_point(current)
            # Encuentra el path más cercano al final del anterior
            next_idx, next_path = min(
                enumerate(remaining),
                key=lambda x: self._distance(last_point, self._get_start_point(x[1]))
            )
            ordered.append(next_path)
            current = next_path
            remaining.pop(next_idx)
        return ordered

    def _get_start_point(self, path):
        if hasattr(path, 'start_point'):
            return path.start_point
        elif hasattr(path, 'points') and path.points:
            return path.points[0]
        elif hasattr(path, '__len__') and hasattr(path, '__getitem__') and len(path) > 0:
            # Path compuesto por segmentos (como svgpathtools.Path)
            segment = path[0]
            if hasattr(segment, 'start'):
                return segment.start
            elif hasattr(segment, 'points') and segment.points:
                return segment.points[0]
        raise AttributeError('Path object has no start_point, points ni segmentos con start')

    def _get_end_point(self, path):
        if hasattr(path, 'end_point'):
            return path.end_point
        elif hasattr(path, 'points') and path.points:
            return path.points[-1]
        elif hasattr(path, '__len__') and hasattr(path, '__getitem__') and len(path) > 0:
            # Path compuesto por segmentos (como svgpathtools.Path)
            segment = path[-1]
            if hasattr(segment, 'end'):
                return segment.end
            elif hasattr(segment, 'points') and segment.points:
                return segment.points[-1]
        raise AttributeError('Path object has no end_point, points ni segmentos con end')

    def _distance(self, p1, p2):
        # Soporta puntos con atributos x/y o números complejos (svgpathtools)
        def get_xy(pt):
            if hasattr(pt, 'x') and hasattr(pt, 'y'):
                return pt.x, pt.y
            elif isinstance(pt, complex):
                return pt.real, pt.imag
            else:
                raise AttributeError('El punto no tiene atributos x/y ni es complejo')
        x1, y1 = get_xy(p1)
        x2, y2 = get_xy(p2)
        return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

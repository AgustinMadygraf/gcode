"""
TrajectoryOptimizer: Reordena paths/segmentos para minimizar movimientos en vacío (greedy).
"""
from typing import List

class TrajectoryOptimizer:
    def optimize_order(self, paths: List) -> List:
        """
        Reordena los paths para minimizar la distancia entre el final de uno y el inicio del siguiente.
        paths: lista de objetos con atributos start_point y end_point.
        """
        if not paths:
            return []
        ordered = []
        remaining = paths[:]
        current = remaining.pop(0)
        ordered.append(current)
        while remaining:
            last_point = current.end_point
            # Encuentra el path más cercano al final del anterior
            next_idx, next_path = min(
                enumerate(remaining),
                key=lambda x: self._distance(last_point, x[1].start_point)
            )
            ordered.append(next_path)
            current = next_path
            remaining.pop(next_idx)
        return ordered

    def _distance(self, p1, p2):
        # Asume que p1 y p2 tienen atributos x, y
        return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2) ** 0.5

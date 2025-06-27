"""
GeometryService: utilidades geométricas para curvatura y simplificación de paths.
"""
from typing import Any, List
import math

class GeometryService:
    def __init__(self):
        pass

    def calculate_curvature(self, path: Any) -> List[float]:
        """
        Calcula la curvatura a lo largo de un path SVG.
        Devuelve una lista de valores de curvatura (uno por punto/segmento).
        """
        curvatures = []
        points = getattr(path, 'points', [])
        for i in range(1, len(points)-1):
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            v1 = (p2.x - p1.x, p2.y - p1.y)
            v2 = (p3.x - p2.x, p3.y - p2.y)
            mag1 = math.hypot(*v1)
            mag2 = math.hypot(*v2)
            if mag1 < 1e-6 or mag2 < 1e-6:
                curvatures.append(0.0)
                continue
            dot = (v1[0]*v2[0] + v1[1]*v2[1]) / (mag1 * mag2)
            dot = max(-1.0, min(1.0, dot))
            angle = math.acos(dot)
            curvatures.append(angle)
        return curvatures

    def simplify_path(self, path: Any, tolerance: float = 0.01) -> Any:
        """
        Simplifica un path SVG usando el algoritmo de reducción de puntos Ramer-Douglas-Peucker.
        (Implementación básica, asume path.points)
        """
        def rdp(points, epsilon):
            if len(points) < 3:
                return points
            # Encuentra el punto más alejado de la línea entre el primero y el último
            start, end = points[0], points[-1]
            max_dist = 0
            idx = 0
            for i in range(1, len(points)-1):
                px, py = points[i].x, points[i].y
                sx, sy = start.x, start.y
                ex, ey = end.x, end.y
                area = abs((ex-sx)*(sy-py) - (sx-px)*(ey-sy))
                length = math.hypot(ex-sx, ey-sy)
                dist = area / (length+1e-8)
                if dist > max_dist:
                    max_dist = dist
                    idx = i
            if max_dist > epsilon:
                left = rdp(points[:idx+1], epsilon)
                right = rdp(points[idx:], epsilon)
                return left[:-1] + right
            else:
                return [start, end]
        if hasattr(path, 'points'):
            new_points = rdp(path.points, tolerance)
            path.points = new_points
        return path

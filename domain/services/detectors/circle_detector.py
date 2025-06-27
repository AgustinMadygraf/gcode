"""
Detector de círculos en paths SVG.
"""
from typing import Optional, Tuple
from svgpathtools import Path
from domain.services.geometry_utils import sample_path_points
import numpy as np

class CircleDetector:
    def try_detect_circle(self, path: Path, tolerance: float = 0.05) -> Optional[Tuple[complex, float]]:
        """
        Intenta detectar si un path es un círculo.
        Args:
            path: Path SVG a analizar
            tolerance: Tolerancia relativa para considerar un círculo (0.05 = 5%)
        Returns:
            Tupla (centro, radio) si es un círculo, None en caso contrario
        """
        if not path.isclosed():
            return None
        num_samples = min(100, max(20, int(path.length() / 5)))
        points = sample_path_points(path, num_samples)
        center_x = np.mean(points[:, 0])
        center_y = np.mean(points[:, 1])
        center = complex(center_x, center_y)
        distances = np.sqrt((points[:, 0] - center_x)**2 + (points[:, 1] - center_y)**2)
        avg_radius = np.mean(distances)
        rel_deviation = np.abs(distances - avg_radius) / avg_radius
        max_deviation = np.max(rel_deviation)
        if max_deviation <= tolerance:
            return center, avg_radius
        return None

"""
BoundingBoxCalculator: Calcula el bounding box, centro, dimensiones y área de rutas SVG.
"""
from typing import Tuple
import numpy as np

class BoundingBoxCalculator:
    "Calcula el bounding box, centro, dimensiones y área de rutas SVG."
    @staticmethod
    def get_svg_bbox(paths) -> Tuple[float, float, float, float]:
        """Calcula el bounding box de los paths SVG."""
        xs, ys = [], []
        for p in paths:
            for seg in p:
                for t in np.linspace(0, 1, 20):
                    z = seg.point(t)
                    xs.append(z.real)
                    ys.append(z.imag)
        if not xs or not ys:
            return 0.0, 0.0, 0.0, 0.0
        return min(xs), max(xs), min(ys), max(ys)


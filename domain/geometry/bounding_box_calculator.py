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
        return min(xs), max(xs), min(ys), max(ys)

    @staticmethod
    def get_center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        " Calcula el centro del bounding box."
        xmin, xmax, ymin, ymax = bbox
        return (xmin + xmax) / 2, (ymin + ymax) / 2

    @staticmethod
    def get_dimensions(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        " Calcula las dimensiones del bounding box."
        xmin, xmax, ymin, ymax = bbox
        return abs(xmax - xmin), abs(ymax - ymin)

    @staticmethod
    def get_area(bbox: Tuple[float, float, float, float]) -> float:
        " Calcula el área del bounding box."
        width, height = BoundingBoxCalculator.get_dimensions(bbox)
        return width * height

"""
BoundingBoxCalculator: Clase utilitaria para calcular el bounding box y centro de paths SVG.
"""
from typing import Tuple

class BoundingBoxCalculator:
    " Clase utilitaria para calcular el bounding box y centro de paths SVG. "
    @staticmethod
    def calculate_bbox(paths) -> Tuple[float, float, float, float]:
        " Calcula el bounding box de una lista de paths SVG. "
        xs, ys = [], []
        for p in paths:
            for seg in p:
                for t in range(21):
                    z = seg.point(t/20)
                    xs.append(z.real)
                    ys.append(z.imag)
        if not xs or not ys:
            raise ValueError("No points found in paths.")
        return min(xs), max(xs), min(ys), max(ys)

    @staticmethod
    def center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        " Calcula el centro del bounding box dado como una tupla (xmin, xmax, ymin, ymax). "
        xmin, xmax, ymin, ymax = bbox
        return (xmin + xmax) / 2, (ymin + ymax) / 2

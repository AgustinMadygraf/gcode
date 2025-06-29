"""
Módulo: primitive_detection_strategy.py

Define una estrategia desacoplada para la detección de primitivas geométricas en paths SVG.
"""
from typing import Optional, List, Any
from domain.models import Point

# from domain.models.svg_path import SVGPath  # Comentado: archivo no existe
SVGPath = Any

class PrimitiveDetectionStrategy:
    def __init__(self, circle_detector, rectangle_detector, ellipse_detector, min_segment_length):
        self.circle_detector = circle_detector
        self.rectangle_detector = rectangle_detector
        self.ellipse_detector = ellipse_detector
        self.min_segment_length = min_segment_length

    def detect(self, svg_path: SVGPath) -> Optional[List[Point]]:
        path = svg_path.path
        # Círculo
        circle_info = self.circle_detector.try_detect_circle(path)
        if circle_info:
            center, radius = circle_info
            from adapters.input.primitive_point_generators import generate_circle_points
            return generate_circle_points(center, radius, self.min_segment_length)
        # Rectángulo
        rect_info = self.rectangle_detector.try_detect_rectangle(path)
        if rect_info:
            corners = rect_info
            return [Point(c.real, c.imag) for c in corners]
        # Elipse
        ellipse_info = self.ellipse_detector.try_detect_ellipse(path)
        if ellipse_info:
            center, rx, ry, phi = ellipse_info
            from adapters.input.primitive_point_generators import generate_ellipse_points
            return generate_ellipse_points(center, rx, ry, phi, self.min_segment_length)
        return None

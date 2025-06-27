"""
Utilidades para generación de puntos de primitivas geométricas (círculo, elipse).
"""
import sys
import os
import numpy as np
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from domain.models import Point

def generate_circle_points(center, radius: float, min_segment_length: float) -> List[Point]:
    """Genera puntos equidistantes para un círculo."""
    n_segments = max(8, int(np.pi * radius / min_segment_length))
    points = [
        Point(center.real + radius * np.cos(2 * np.pi * i / n_segments),
              center.imag + radius * np.sin(2 * np.pi * i / n_segments))
        for i in range(n_segments)
    ]
    points.append(points[0])  # Cierra el círculo
    return points

def generate_ellipse_points(center, rx: float, ry: float, phi: float, min_segment_length: float) -> List[Point]:
    """Genera puntos equidistantes para una elipse rotada."""
    perimeter = np.pi * (3*(rx + ry) - np.sqrt((3*rx + ry) * (rx + 3*ry)))
    n_segments = max(8, int(perimeter / min_segment_length))
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    points = []
    for i in range(n_segments):
        angle = 2 * np.pi * i / n_segments
        x0 = rx * np.cos(angle)
        y0 = ry * np.sin(angle)
        x = center.real + x0 * cos_phi - y0 * sin_phi
        y = center.imag + x0 * sin_phi + y0 * cos_phi
        points.append(Point(x, y))
    points.append(points[0])  # Cierra la elipse
    return points

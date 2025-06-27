"""
Utilidades geométricas compartidas para detectores de formas SVG.
"""
from typing import List, Tuple
import numpy as np
from svgpathtools import Path, Line

def simplify_path_lines(path: Path) -> Path:
    """
    Simplifica un path combinando líneas colineales.
    """
    if len(path) <= 1:
        return path
    new_segments = [path[0]]
    for i in range(1, len(path)):
        prev_segment = new_segments[-1]
        current_segment = path[i]
        if not (isinstance(prev_segment, Line) and isinstance(current_segment, Line)):
            new_segments.append(current_segment)
            continue
        prev_dir = prev_segment.end - prev_segment.start
        curr_dir = current_segment.end - current_segment.start
        prev_mag = abs(prev_dir)
        curr_mag = abs(curr_dir)
        if prev_mag < 1e-10 or curr_mag < 1e-10:
            new_segments.append(current_segment)
            continue
        prev_dir_norm = prev_dir / prev_mag
        curr_dir_norm = curr_dir / curr_mag
        cross_product = prev_dir_norm.real * curr_dir_norm.imag - prev_dir_norm.imag * curr_dir_norm.real
        if abs(cross_product) < 1e-6:
            new_segments[-1] = Line(prev_segment.start, current_segment.end)
        else:
            new_segments.append(current_segment)
    return Path(*new_segments)

def sample_path_points(path: Path, num_samples: int = 100) -> np.ndarray:
    """
    Muestrea puntos equidistantes a lo largo de un path SVG.
    """
    points = []
    for i in range(num_samples):
        t = i / num_samples
        point = path.point(t)
        points.append((point.real, point.imag))
    return np.array(points)

"""
Detector de rectángulos en paths SVG.
"""
from typing import Optional, List
from svgpathtools import Path
from domain.services.geometry_utils import simplify_path_lines
import numpy as np
from svgpathtools import Line

class RectangleDetector:
    def try_detect_rectangle(self, path: Path, angle_tol: float = 5.0, ratio_tol: float = 0.05) -> Optional[List[complex]]:
        """
        Intenta detectar si un path es un rectángulo.
        Args:
            path: Path SVG a analizar
            angle_tol: Tolerancia en grados para ángulos rectos
            ratio_tol: Tolerancia para comparación de lados opuestos
        Returns:
            Lista de esquinas si es un rectángulo, None en caso contrario
        """
        if not path.isclosed():
            return None
        if len(path) % 4 != 0 or len(path) < 4:
            return None
        if len(path) > 4:
            for segment in path:
                if not isinstance(segment, Line):
                    return None
            path = simplify_path_lines(path)
            if len(path) != 4:
                return None
        corners = [path[0].start]
        for i in range(4):
            segment = path[i]
            if not isinstance(segment, Line):
                return None
            corners.append(segment.end)
            next_segment = path[(i + 1) % 4]
            current_dir = segment.end - segment.start
            next_dir = next_segment.end - next_segment.start
            dot_product = (current_dir.real * next_dir.real + current_dir.imag * next_dir.imag)
            current_mag = abs(current_dir)
            next_mag = abs(next_dir)
            if current_mag < 1e-10 or next_mag < 1e-10:
                return None
            cos_angle = dot_product / (current_mag * next_mag)
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            if abs(angle_deg - 90) > angle_tol:
                return None
        len1 = abs(path[0].end - path[0].start)
        len2 = abs(path[2].end - path[2].start)
        len3 = abs(path[1].end - path[1].start)
        len4 = abs(path[3].end - path[3].start)
        if abs(len1 - len2) / max(len1, len2) > ratio_tol or abs(len3 - len4) / max(len3, len4) > ratio_tol:
            return None
        return corners[:4]

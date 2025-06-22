"""
SvgBorderDetector: Detecta si un path representa el borde/marco de un documento SVG
"""
import math
from typing import Dict

class SvgBorderDetector:
    """Detecta si un path representa el marco rectangular de un SVG."""
    
    def __init__(self, tolerance: float = 0.05):
        """
        Inicializa el detector con una tolerancia para comparar dimensiones.
        Args:
            tolerance: Porcentaje (0-1) de variación permitida al comparar dimensiones
        """
        self.tolerance = tolerance
        
    def is_rectangle(self, path) -> bool:
        """Determina si un path forma un rectángulo cerrado."""
        if len(path) != 4:  # Un rectángulo típicamente tiene 4 segmentos
            return False
        
        # Verificar si es cerrado (primer punto = último punto)
        if abs(path[0].start - path[-1].end) > 1e-6:
            return False
        
        # Verificar si tiene 4 ángulos cercanos a 90 grados
        for i in range(4):
            seg1 = path[i]
            seg2 = path[(i + 1) % 4]
            dir1 = seg1.end - seg1.start
            dir2 = seg2.end - seg2.start
            dot = (dir1.real * dir2.real + dir1.imag * dir2.imag)
            mag1 = math.sqrt(dir1.real**2 + dir1.imag**2)
            mag2 = math.sqrt(dir2.real**2 + dir2.imag**2)
            if mag1 == 0 or mag2 == 0:
                return False
            cos_angle = dot / (mag1 * mag2)
            if abs(cos_angle) > 0.1:  # Permitimos pequeña desviación
                return False
        return True
    
    def matches_svg_bounds(self, path, svg_attr: Dict) -> bool:
        """Determina si el rectángulo coincide con el viewBox del SVG."""
        if not self.is_rectangle(path):
            return False
        points = [seg.start for seg in path] + [path[-1].end]
        x_coords = [p.real for p in points]
        y_coords = [p.imag for p in points]
        path_xmin, path_xmax = min(x_coords), max(x_coords)
        path_ymin, path_ymax = min(y_coords), max(y_coords)
        vb = svg_attr.get("viewBox")
        if vb:
            vb_parts = list(map(float, vb.split()))
            if len(vb_parts) == 4:
                vb_x, vb_y, vb_width, vb_height = vb_parts
                vb_xmin, vb_ymin = vb_x, vb_y
                vb_xmax, vb_ymax = vb_x + vb_width, vb_y + vb_height
                x_match = (abs(path_xmin - vb_xmin) < self.tolerance * vb_width and 
                           abs(path_xmax - vb_xmax) < self.tolerance * vb_width)
                y_match = (abs(path_ymin - vb_ymin) < self.tolerance * vb_height and
                           abs(path_ymax - vb_ymax) < self.tolerance * vb_height)
                return x_match and y_match
        return False

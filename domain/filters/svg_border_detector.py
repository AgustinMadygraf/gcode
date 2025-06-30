"""
SvgBorderDetector: Detecta si un path representa el borde/marco de un documento SVG
"""
import math
from typing import Dict
import logging

class SvgBorderDetector:
    """
    Detecta si un path representa el marco rectangular de un SVG.
    La detección compara los márgenes del path con el viewBox usando una tolerancia relativa configurable.
    Si todos los bordes del path están dentro de la tolerancia respecto al viewBox, se considera borde.
    """
    
    def __init__(self, tolerance: float = 0.05, logger=None):
        """
        Inicializa el detector con una tolerancia para comparar dimensiones.
        Args:
            tolerance: Proporción (0-1) de variación permitida al comparar dimensiones respecto al tamaño del viewBox.
            logger: Logger inyectado. Debe ser un objeto compatible con logging.Logger.
        """
        self.tolerance = tolerance
        if logger is None:
            raise RuntimeError("Logger debe ser inyectado en SvgBorderDetector. Usar siempre el constructor con logger explícito.")
        self.logger = logger
    
    def is_rectangle(self, path) -> bool:
        """Determina si un path forma un rectángulo cerrado."""
        if len(path) != 4:  # Un rectángulo típicamente tiene 4 segmentos
            self.logger.debug(f"No es rectángulo: segmentos={len(path)}")
            return False
        
        # Verificar si es cerrado (primer punto = último punto)
        if abs(path[0].start - path[-1].end) > 1e-6:
            self.logger.debug("No es rectángulo: no está cerrado")
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
                self.logger.debug(f"No es rectángulo: segmento {i} de longitud cero")
                return False
            cos_angle = dot / (mag1 * mag2)
            if abs(cos_angle) > 0.1:  # Permitimos pequeña desviación
                self.logger.debug(f"No es rectángulo: ángulo {i} no es 90° (cos={cos_angle:.3f})")
                return False
        self.logger.debug("Path es un rectángulo cerrado")
        return True
    
    def matches_svg_bounds(self, path, svg_attr: Dict) -> bool:
        """
        Determina si el path rectangular coincide con el viewBox del SVG dentro de la tolerancia relativa.
        Args:
            path: Path de svgpathtools (o similar) que debe ser un rectángulo cerrado.
            svg_attr: Diccionario con atributos del SVG, debe incluir 'viewBox'.
        Returns:
            True si el path coincide con el marco del SVG, False en caso contrario.
        """
        if not self.is_rectangle(path):
            self.logger.debug("Descartado: no es rectángulo")
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
                self.logger.debug(f"Comparando path: xmin={path_xmin:.3f}, xmax={path_xmax:.3f}, ymin={path_ymin:.3f}, ymax={path_ymax:.3f}")
                self.logger.debug(f"Con viewBox: xmin={vb_xmin:.3f}, xmax={vb_xmax:.3f}, ymin={vb_ymin:.3f}, ymax={vb_ymax:.3f}, tol={self.tolerance}")
                self.logger.debug(f"x_match={x_match}, y_match={y_match}")
                return x_match and y_match
        self.logger.debug("Descartado: no hay viewBox válido")
        return False
    
    def __getstate__(self):
        state = self.__dict__.copy()
        # No serializar el logger
        state['logger'] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # No restaurar el logger automáticamente; debe ser reinyectado tras deserializar
        self.logger = None

    def __delattr__(self, name):
        if name == 'logger':
            raise AttributeError("No se permite eliminar el logger de SvgBorderDetector")
        super().__delattr__(name)

"""
SvgBorderDetector: Detecta si un path representa el borde/marco de un documento SVG
"""
import math
from typing import Dict

class SvgBorderDetector:
    DEBUG_ENABLED = False  # Controla si se muestran logs debug
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

    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED:
            self.logger.debug(msg, *args, **kwargs)

    def is_rectangle(self, path) -> bool:
        """Determina si un path forma un rectángulo cerrado."""
        if len(path) != 4:  # Un rectángulo típicamente tiene 4 segmentos
            msg = f"No es rectángulo: segmentos={len(path)}"
            self._debug(msg)
            return False

        # Verificar si es cerrado (primer punto = último punto)
        if abs(path[0].start - path[-1].end) > 1e-6:
            msg = "No es rectángulo: no está cerrado"
            self._debug(msg)
            return False

        # Verificar si tiene 4 ángulos cercanos a 90 grados
        for i in range(4):
            seg1 = path[i]
            seg2 = path[(i + 1) % 4]
            dir1 = seg1.end - seg1.start
            dir2 = seg2.end - seg2.start
            dot = dir1.real * dir2.real + dir1.imag * dir2.imag
            mag1 = math.sqrt(dir1.real**2 + dir1.imag**2)
            mag2 = math.sqrt(dir2.real**2 + dir2.imag**2)
            if mag1 == 0 or mag2 == 0:
                msg = f"No es rectángulo: segmento {i} de longitud cero"
                self._debug(msg)
                return False
            cos_angle = dot / (mag1 * mag2)
            if abs(cos_angle) > 0.1:  # Permitimos pequeña desviación
                msg = f"No es rectángulo: ángulo {i} no es 90° (cos={cos_angle:.3f})"
                self._debug(msg)
                return False
        msg = "Path es un rectángulo cerrado"
        self._debug(msg)
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
        self._debug(f"[matches_svg_bounds] Llamado con path de {len(path)} segmentos y svg_attr={svg_attr}")
        if not self.is_rectangle(path):
            self._debug("Descartado: no es rectángulo")
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
            else:
                msg = f"viewBox no tiene 4 valores: {vb}"
                self._debug(msg)
                return False
        else:
            # Si no hay viewBox, intentar con width/height
            try:
                vb_xmin = 0.0
                vb_ymin = 0.0
                vb_xmax = float(svg_attr.get("width"))
                vb_ymax = float(svg_attr.get("height"))
                vb_width = vb_xmax - vb_xmin
                vb_height = vb_ymax - vb_ymin
                msg = f"Usando width/height como viewBox: xmin={vb_xmin}, xmax={vb_xmax}, ymin={vb_ymin}, ymax={vb_ymax}"
                self._debug(msg)
            except (ValueError, TypeError):
                self.logger.error("Descartado: no hay viewBox válido ni width/height")
                return False
        x_match = (abs(path_xmin - vb_xmin) < self.tolerance * vb_width and
                   abs(path_xmax - vb_xmax) < self.tolerance * vb_width)
        y_match = (abs(path_ymin - vb_ymin) < self.tolerance * vb_height and
                   abs(path_ymax - vb_ymax) < self.tolerance * vb_height)
        msg1 = f"Comparando path: xmin={path_xmin:.3f}, xmax={path_xmax:.3f}, ymin={path_ymin:.3f}, ymax={path_ymax:.3f}"
        msg2 = f"Con viewBox: xmin={vb_xmin:.3f}, xmax={vb_xmax:.3f}, ymin={vb_ymin:.3f}, ymax={vb_ymax:.3f}, tol={self.tolerance}"
        msg3 = f"x_match={x_match}, y_match={y_match}"
        self._debug(msg1)
        self._debug(msg2)
        self._debug(msg3)
        if not x_match:
            msg = (
                f"No coincide en X: "
                f"|{path_xmin} - {vb_xmin}|="
                f"{abs(path_xmin-vb_xmin):.3f}, "
                f"|{path_xmax} - {vb_xmax}|="
                f"{abs(path_xmax-vb_xmax):.3f} "
                f"(tol={self.tolerance * vb_width:.3f})"
            )
            self._debug(msg)
        if not y_match:
            msg = (
                f"No coincide en Y: "
                f"|{path_ymin} - {vb_ymin}|="
                f"{abs(path_ymin-vb_ymin):.3f}, "
                f"|{path_ymax} - {vb_ymax}|="
                f"{abs(path_ymax-vb_ymax):.3f} "
                f"(tol={self.tolerance * vb_height:.3f})"
            )
            self._debug(msg)
        if x_match and y_match:
            self._debug("Path identificado como borde del SVG")
            self._debug("Path coincide con el marco del SVG (borde)")
            return True
        else:
            # Si es rectángulo pero no coincide, advertir
            if self.is_rectangle(path):
                self.logger.warning("Rectángulo detectado pero no coincide con el borde del SVG (puede ser un marco interno o error de tolerancia)")
            self._debug("Path NO coincide con el marco del SVG (no borde)")
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

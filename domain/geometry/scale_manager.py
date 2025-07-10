"""
ScaleManager: Encapsula lógica de escalado SVG y validaciones.
"""
from typing import Dict
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator

class ScaleManager:
    """
    Clase para manejar el escalado de SVGs y G-code, incluyendo validaciones de dimensiones.
    El debug se controla mediante un flag en la configuración pasada como dependencia.
    Ahora soporta logger opcional.
    """
    def __init__(self, config_provider=None, logger=None):
        """
        :param config_provider: objeto con método get_debug_flag(str), puede ser None para desactivar debug.
        :param logger: logger opcional para debug.
        """
        self.config_provider = config_provider
        self.logger = logger
        self.config = config_provider

    def _debug(self, msg, *args, **kwargs):
        debug_enabled = False
        if self.config and hasattr(self.config, "get_debug_flag"):
            debug_enabled = self.config.get_debug_flag("ScaleManager")
        if debug_enabled and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def _parse_length(self, length_str: str) -> float:
        """Convierte un string de longitud SVG a milímetros (mm)."""
        if length_str.endswith("mm"):
            return float(length_str[:-2])
        elif length_str.endswith("cm"):
            return float(length_str[:-2]) * 10.0
        elif length_str.endswith("in"):
            return float(length_str[:-2]) * 25.4
        elif length_str.endswith("px"):
            # Asume 1 px = 1 px (sin conversión)
            return float(length_str[:-2])
        else:
            # Si no hay unidad, asume px
            return float(length_str)

    def viewbox_scale(self, svg_attr: Dict) -> float:
        " Calcula el factor de escala basado en el viewBox y el ancho del SVG. "
        vb = svg_attr.get("viewBox")
        width = svg_attr.get("width")
        if vb and width:
            try:
                _, _, vb_w, _ = map(float, vb.split())
                width_mm = self._parse_length(width)
                self._debug(f"viewbox_scale: vb_w={vb_w}, width_mm={width_mm}")
                if width.endswith("mm") or width.endswith("cm") or width.endswith("in"):
                    vb_w_mm = vb_w * 25.4 / 96.0
                    self._debug(f"viewbox_scale: vb_w_mm={vb_w_mm}")
                    scale = width_mm / vb_w_mm
                else:
                    scale = width_mm / vb_w
                self._debug(f"viewbox_scale: scale={scale}")
                if scale <= 0 or not scale or scale != scale:
                    raise ValueError("Escala inválida calculada")
                return scale
            except Exception as exc:
                self._debug(f"viewbox_scale: error {exc}")
                raise ValueError("Atributos SVG inválidos para calcular escala") from exc
        return 1.0

    def adjust_scale_for_max_height(self, paths, scale: float, max_height_mm: float) -> float:
        " Ajusta el factor de escala para que la altura no supere max_height_mm. "
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        _, _, ymin, ymax = bbox
        height = abs(ymax - ymin) * scale
        self._debug(f"adjust_scale_for_max_height: bbox={bbox}, height={height}, max_height_mm={max_height_mm}, scale_in={scale}")
        if height > max_height_mm:
            factor = max_height_mm / (abs(ymax - ymin) * scale)
            scale = scale * factor
            self._debug(f"adjust_scale_for_max_height: factor={factor}, scale_out={scale}")
        if scale <= 0 or not scale or scale != scale:
            raise ValueError("Escala final inválida")
        return scale

    def adjust_scale_for_max_width(self, paths, scale: float, max_width_mm: float) -> float:
        """Ajusta el factor de escala para que el ancho no supere max_width_mm."""
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        xmin, xmax, _, _ = bbox
        width = abs(xmax - xmin) * scale
        self._debug(f"adjust_scale_for_max_width: bbox={bbox}, width={width}, max_width_mm={max_width_mm}, scale_in={scale}")
        if width > max_width_mm:
            factor = max_width_mm / (abs(xmax - xmin) * scale)
            scale = scale * factor
            self._debug(f"adjust_scale_for_max_width: factor={factor}, scale_out={scale}")
        if scale <= 0 or not scale or scale != scale:
            raise ValueError("Escala final inválida")
        return scale

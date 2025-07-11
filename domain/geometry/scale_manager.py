"""
ScaleManager: Encapsula lógica de escalado SVG y validaciones.
"""

from typing import Dict
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator
from infrastructure.logger_helper import LoggerHelper

class ScaleManager(LoggerHelper):
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
        super().__init__(config=config_provider, logger=logger)
        self.config_provider = config_provider
        self.config = config_provider

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
        height_base = abs(ymax - ymin)
        height = height_base * scale
        self._debug(f"adjust_scale_for_max_height: bbox={bbox}, height={height:.4g}, max_height_mm={max_height_mm:.4g}, scale_in={scale:.4g}")
        self._debug(f"adjust_scale_for_max_height: height_used={height_base:.4g}, height_scaled={height:.4g}, scale_in={scale:.4g}")
        if height > max_height_mm:
            factor = max_height_mm / height
            self._debug(f"adjust_scale_for_max_height: factor={factor:.4g}, scale_out={(scale * factor):.4g}")
            scale = scale * factor
        if scale <= 0 or not scale or scale != scale:
            raise ValueError("Escala final inválida")
        final_height = abs(ymax - ymin) * scale
        # INFO eliminado, se unificará tras ambos ajustes
        self._debug(f"adjust_scale_for_max_height: FINAL height={final_height:.4g}mm, scale_final={scale:.4g}")
        return scale

    def adjust_scale_for_max_width(self, paths, scale: float, max_width_mm: float) -> float:
        """Ajusta el factor de escala para que el ancho no supere max_width_mm."""
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        xmin, xmax, _, _ = bbox
        width_base = abs(xmax - xmin)
        width = width_base * scale
        self._debug(f"adjust_scale_for_max_width: bbox={bbox}, width={width:.4g}, max_width_mm={max_width_mm:.4g}, scale_in={scale:.4g}")
        self._debug(f"adjust_scale_for_max_width: width_used={width_base:.4g}, width_scaled={width:.4g}, scale_in={scale:.4g}")
        if width > max_width_mm:
            factor = max_width_mm / width
            self._debug(f"adjust_scale_for_max_width: factor={factor:.4g}, scale_out={(scale * factor):.4g}")
            scale = scale * factor
        if scale <= 0 or not scale or scale != scale:
            raise ValueError("Escala final inválida")
        final_width = abs(xmax - xmin) * scale
        # INFO eliminado, se unificará tras ambos ajustes
        self._debug(f"adjust_scale_for_max_width: FINAL width={final_width:.4g}mm, scale_final={scale:.4g}")
        return scale

    def apply_scaling(self, paths, svg_attr: Dict, max_height_mm: float, max_width_mm: float) -> float:
        " Aplica el escalado a los paths basado en los atributos del SVG y las dimensiones máximas. "
        self.logger.info(f"ScaleManager: máximos usados: ancho={max_width_mm:.4g}mm, alto={max_height_mm:.4g}mm")

        scale = self.viewbox_scale(svg_attr)
        self._debug(f"apply_scaling: scale tras viewbox_scale={scale}")
        scale = self.adjust_scale_for_max_height(paths, scale, max_height_mm)
        scale = self.adjust_scale_for_max_width(paths, scale, max_width_mm)

        # Calcula el bbox final con el scale definitivo
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        xmin, xmax, ymin, ymax = bbox
        final_width = abs(xmax - xmin) * scale
        final_height = abs(ymax - ymin) * scale

        # Loguea el INFO con ambos valores (máximo 4 dígitos)
        self.logger.info(f"Estimado: ancho={final_width:.4g}mm, alto={final_height:.4g}mm")
        return scale

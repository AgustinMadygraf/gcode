"""
ScaleManager: Encapsula lógica de escalado SVG y validaciones.
"""
from typing import Dict
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator

class ScaleManager:
    @staticmethod
    def _parse_length(length_str: str) -> float:
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

    @staticmethod
    def viewbox_scale(svg_attr: Dict) -> float:
        vb = svg_attr.get("viewBox")
        width = svg_attr.get("width")
        if vb and width:
            try:
                _, _, vb_w, _ = map(float, vb.split())
                width_mm = ScaleManager._parse_length(width)
                # Si el viewBox está en px y el width en mm, convierte px a mm (asume 96 px/inch)
                # Pero si ambos están en mm, la escala será 1
                # Aquí asumimos que viewBox siempre está en px, y width puede estar en mm/cm/in/px
                # Por lo general, SVG usa px en viewBox
                # Para convertir px a mm: 1 px = 25.4 / 96 mm
                if width.endswith("mm") or width.endswith("cm") or width.endswith("in"):
                    vb_w_mm = vb_w * 25.4 / 96.0
                    scale = width_mm / vb_w_mm
                else:
                    scale = width_mm / vb_w
                if scale <= 0 or not scale or scale != scale:
                    raise ValueError("Escala inválida calculada")
                return scale
            except Exception as exc:
                raise ValueError("Atributos SVG inválidos para calcular escala") from exc
        return 1.0

    @staticmethod
    def adjust_scale_for_max_height(paths, scale: float, max_height_mm: float) -> float:
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        _, _, ymin, ymax = bbox
        height = abs(ymax - ymin) * scale
        if height > max_height_mm:
            factor = max_height_mm / (abs(ymax - ymin) * scale)
            scale = scale * factor
        if scale <= 0 or not scale or scale != scale:
            raise ValueError("Escala final inválida")
        return scale

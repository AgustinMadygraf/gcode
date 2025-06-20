"""
ScaleManager: Encapsula lógica de escalado SVG y validaciones.
"""
from typing import Dict
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator

class ScaleManager:
    @staticmethod
    def viewbox_scale(svg_attr: Dict) -> float:
        vb = svg_attr.get("viewBox")
        width = svg_attr.get("width")
        if vb and width:
            try:
                _, _, vb_w, _ = map(float, vb.split())
                width_px = float(width.rstrip("px"))
                scale = width_px / vb_w
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

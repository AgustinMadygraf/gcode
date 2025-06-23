"""
Servicio de aplicación para generación de G-code a partir de paths y atributos SVG.
(Movido desde domain/gcode_generation_service.py)
"""
from typing import List, Any
from domain.gcode_generator import GCodeGenerator

class GCodeGenerationService:
    " Servicio de aplicación para generación de G-code a partir de paths y atributos SVG. "
    def __init__(self, generator: GCodeGenerator):
        self.generator = generator

    def generate(self, paths: List[Any], svg_attr: dict) -> List[str]:
        """
        Genera las líneas de G-code a partir de los paths y atributos SVG.
        """
        return self.generator.generate(paths, svg_attr)

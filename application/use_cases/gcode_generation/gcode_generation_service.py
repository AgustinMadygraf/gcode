"""
Servicio de aplicación para generación de G-code a partir de paths y atributos SVG.
(Movido desde domain/gcode_generation_service.py)
"""
from typing import List, Any
from domain.ports.gcode_generator_port import GcodeGeneratorPort

class GCodeGenerationService:
    " Servicio de aplicación para generación de G-code a partir de paths y atributos SVG. "
    def __init__(self, generator: GcodeGeneratorPort):
        self.generator = generator

    def generate(self, paths: List[Any], svg_attr: dict, context=None) -> List[str]:
        """
        Genera las líneas de G-code a partir de los paths y atributos SVG.
        """
        # Usar el método global del adaptador para optimización y logs
        return self.generator.generate(paths, svg_attr)

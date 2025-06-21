"""
LegacyGcodeGeneratorAdapter
Mantiene la API antigua de GcodeGenerator para compatibilidad durante la refactorización.
"""

from domain.gcode_generator import GCodeGenerator

class LegacyGcodeGeneratorAdapter:
    def __init__(self, *args, **kwargs):
        self._gcode_generator = GCodeGenerator(*args, **kwargs)

    def generate(self, *args, **kwargs):
        return self._gcode_generator.generate(*args, **kwargs)

    # Agrega aquí otros métodos legacy necesarios para compatibilidad

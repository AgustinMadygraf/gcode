"""
LegacyGcodeGeneratorAdapter
Mantiene la API antigua de GcodeGenerator para compatibilidad durante la refactorización.
"""

from domain.gcode_generator import GCodeGenerator
from infrastructure.path_sampler import PathSampler

class LegacyGcodeGeneratorAdapter:
    def __init__(self, *args, **kwargs):
        # Extraer step_mm y logger de kwargs si existen
        step_mm = kwargs.get('step_mm', 0.3)
        logger = kwargs.get('logger', None)
        path_sampler = PathSampler(step_mm, logger=logger)
        kwargs['path_sampler'] = path_sampler
        self._gcode_generator = GCodeGenerator(*args, **kwargs)

    def generate(self, *args, **kwargs):
        return self._gcode_generator.generate(*args, **kwargs)

    # Agrega aquí otros métodos legacy necesarios para compatibilidad

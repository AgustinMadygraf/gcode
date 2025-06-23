"""
LegacyGcodeGeneratorAdapter
Mantiene la API antigua de GcodeGenerator para compatibilidad durante la refactorización.
"""

from domain.gcode_generator import GCodeGenerator
from infrastructure.path_sampler import PathSampler
from infrastructure.optimizers.arc_optimizer import ArcOptimizer
from infrastructure.optimizers.colinear_optimizer import ColinearOptimizer

class LegacyGcodeGeneratorAdapter:
    def __init__(self, *args, **kwargs):
        # Extraer step_mm y logger de kwargs si existen
        step_mm = kwargs.get('step_mm', 0.3)
        logger = kwargs.get('logger', None)
        path_sampler = PathSampler(step_mm, logger=logger)
        kwargs['path_sampler'] = path_sampler
        self._gcode_generator = GCodeGenerator(*args, **kwargs)
        self.arc_optimizer = ArcOptimizer()
        self.colinear_optimizer = ColinearOptimizer()

    def generate(self, *args, **kwargs):
        gcode_lines = self._gcode_generator.generate(*args, **kwargs)
        # Las métricas ya se muestran por logger en GCodeGenerator
        if hasattr(self._gcode_generator, 'last_metrics'):
            print(f"Métricas de optimización: {self._gcode_generator.last_metrics}")
        return gcode_lines

    # Agrega aquí otros métodos legacy necesarios para compatibilidad

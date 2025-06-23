"""
Script para imprimir y analizar el flujo de comandos G-code generado para varios trazos.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.output.gcode_generator_adapter import GCodeGeneratorImpl
from domain.path_transform_strategy import PathTransformStrategy
from infrastructure.optimizers.optimization_chain import OptimizationChain
from application.generation.optimizer_factory import make_optimization_chain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService  # Importar el servicio

class DummySegment:
    def __init__(self, length, start=(0,0), end=(1,0)):
        self._length = length
        self._start = start
        self._end = end
    def length(self):
        return self._length
    def point(self, t):
        x = self._start[0] + (self._end[0] - self._start[0]) * t
        y = self._start[1] + (self._end[1] - self._start[1]) * t
        return complex(x, y)

class DummyStrategy(PathTransformStrategy):
    def transform(self, x, y):
        return x, y

def print_gcode_for_multiple_strokes():
    seg1 = DummySegment(5, (0,0), (5,0))
    seg2 = DummySegment(5, (10,0), (15,0))
    paths = [[seg1], [seg2]]  # Dos trazos separados
    svg_attr = {"viewBox": "0 0 20 10", "width": "20"}
    generator = GCodeGeneratorImpl(
        feed=1000,
        cmd_down="M3 S1000",
        cmd_up="M5",
        step_mm=5,
        dwell_ms=100,
        max_height_mm=10,
        logger=None,
        transform_strategies=[DummyStrategy()],
        optimizer=OptimizationChain()  # Inyectar la cadena de optimización
    )
    gcode_service = GCodeGenerationService(generator)
    # Imprimir puntos de inicio y fin de cada trazo
    all_points = generator.get_points_for_paths(paths, 1.0)
    for i, points in enumerate(all_points):
        if points:
            print(f"Trazo {i+1}: inicio=({points[0].x:.3f}, {points[0].y:.3f}), fin=({points[-1].x:.3f}, {points[-1].y:.3f})")
    print("\n--- G-code generado ---")
    gcode = gcode_service.generate(paths, svg_attr)
    for i, line in enumerate(gcode):
        print(f"{i:03d}: {line}")

if __name__ == "__main__":
    print_gcode_for_multiple_strokes()

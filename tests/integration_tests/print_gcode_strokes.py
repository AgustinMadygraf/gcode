class DummyI18n:
    def get(self, key, **kwargs):
        return key
class DummyLogger:
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass

"""
Script para imprimir y analizar el flujo de comandos G-code generado para varios trazos.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.path_transform_strategy import PathTransformStrategy
from domain.services.optimization.optimization_chain import OptimizationChain
from application.generation.optimizer_factory import make_optimization_chain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService  # Importar el servicio
from tests.mocks.mock_geometry import DummySegment
from tests.mocks.mock_strategy import DummyStrategy

def print_gcode_for_multiple_strokes():
    seg1 = DummySegment(5, (0,0), (5,0))
    seg2 = DummySegment(5, (10,0), (15,0))
    paths = [[seg1], [seg2]]  # Dos trazos separados
    svg_attr = {"viewBox": "0 0 20 10", "width": "20"}
    # Definir plotter_max_area_mm localmente (simula config)
    plotter_max_area_mm = [180.0, 250.0]
    generator = GCodeGeneratorAdapter(
        path_sampler=None,  # Ajusta si tienes un path_sampler adecuado
        feed=1000,
        cmd_down="M3 S1000",
        cmd_up="M5",
        step_mm=5,
        dwell_ms=100,
        max_height_mm=plotter_max_area_mm[1],
        logger=DummyLogger(),
        i18n=DummyI18n(),
        transform_strategies=[DummyStrategy()],
        optimizer=OptimizationChain(),
        config=None  # Ajusta si tienes un config adecuado
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

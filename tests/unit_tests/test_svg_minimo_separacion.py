"""
Test automatizado para validar la separación de trazos en el G-code generado a partir de un SVG mínimo.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from infrastructure.svg_loader import SvgLoaderAdapter
from infrastructure.adapters.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.path_transform_strategy import PathTransformStrategy
from config.config import CMD_DOWN, CMD_UP, FEED, STEP_MM, DWELL_MS, MAX_HEIGHT_MM
from infrastructure.optimizers.optimization_chain import OptimizationChain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from domain.ports.path_sampler_port import PathSamplerPort
from domain.entities.point import Point

class MockStrategy(PathTransformStrategy):
    def transform(self, x, y):
        return x, y

class MockPathSampler(PathSamplerPort):
    def sample(self, path):
        # Convierte los segmentos del path en una lista de Point
        points = []
        for seg in path:
            # samplea 2 puntos por segmento (inicio y fin)
            z0 = seg.point(0)
            z1 = seg.point(1)
            points.append(Point(z0.real, z0.imag))
            points.append(Point(z1.real, z1.imag))
        return points

class TestSVGMinimoSeparacion(unittest.TestCase):
    def test_separacion_trazos_svg_minimo(self):
        from pathlib import Path
        svg_file = (Path(__file__).parent.parent / "svg_input" / "test_lines.svg").resolve()
        svg = SvgLoaderAdapter(svg_file)
        paths = svg.get_paths()
        svg_attr = svg.get_attributes()
        generator = GCodeGeneratorAdapter(
            path_sampler=MockPathSampler(),
            feed=FEED,
            cmd_down=CMD_DOWN,
            cmd_up=CMD_UP,
            step_mm=STEP_MM,
            dwell_ms=DWELL_MS,
            max_height_mm=MAX_HEIGHT_MM,
            logger=None,
            transform_strategies=[MockStrategy()],
            optimizer=OptimizationChain()  # Inyectar la cadena de optimización
        )
        gcode_service = GCodeGenerationService(generator)
        gcode = gcode_service.generate(paths, svg_attr)
        # Buscar los índices de los comandos CMD_DOWN y CMD_UP
        down_indices = [i for i, line in enumerate(gcode) if line.strip() == CMD_DOWN]
        up_indices = [i for i, line in enumerate(gcode) if line.strip() == CMD_UP]
        # Debe haber al menos dos pares CMD_DOWN/CMD_UP (dos trazos)
        self.assertGreaterEqual(len(down_indices), 2)
        self.assertGreaterEqual(len(up_indices), 2)
        # Verificar que entre cada par CMD_DOWN/CMD_UP solo haya G1 y no G0
        for d in down_indices:
            # Buscar el siguiente CMD_UP después de este CMD_DOWN
            u = next((i for i in up_indices if i > d), None)
            if u is not None:
                lines_between = gcode[d+1:u]
                # Permitir un G0 inicial tras CMD_DOWN
                if lines_between and lines_between[0].startswith("G0"):
                    lines_between = lines_between[1:]
                for line in lines_between:
                    self.assertTrue(
                        line.startswith("G1") or line.startswith("G4"),
                        f"Comando inesperado entre CMD_DOWN y CMD_UP: {line}"
                    )
        # Verificar que entre CMD_UP y el siguiente CMD_DOWN haya un G0
        for u in up_indices:
            # Buscar el siguiente CMD_DOWN después de este CMD_UP
            d = next((i for i in down_indices if i > u), None)
            if d is not None:
                has_g0 = any(line.startswith("G0") for line in gcode[u:d])
                self.assertTrue(has_g0, "Falta G0 entre CMD_UP y CMD_DOWN")

if __name__ == "__main__":
    unittest.main()

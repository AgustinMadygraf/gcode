"""
Test automatizado para validar la separación de trazos en el G-code generado a partir de un SVG mínimo.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.input.svg_loader_adapter import SvgLoaderAdapter
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.path_transform_strategy import PathTransformStrategy
from infrastructure.config.config import Config
from domain.services.optimization.optimization_chain import OptimizationChain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from domain.ports.path_sampler_port import PathSamplerPort
from domain.entities.point import Point
import pytest

@pytest.fixture(scope="module")
def config():
    return Config()

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

class TestMinimumSeparationSVG(unittest.TestCase):
    def test_minimum_stroke_separation(self):
        from pathlib import Path
        config = Config()
        svg_file = (Path(__file__).parent.parent / "svg_input" / "test_lines.svg").resolve()
        svg = SvgLoaderAdapter(svg_file)
        paths = svg.get_paths()
        svg_attr = svg.get_attributes()
        generator = GCodeGeneratorAdapter(
            path_sampler=MockPathSampler(),
            feed=config.feed,
            cmd_down=config.cmd_down,
            cmd_up=config.cmd_up,
            step_mm=config.step_mm,
            dwell_ms=config.dwell_ms,
            max_height_mm=config.max_height_mm,
            logger=None,
            transform_strategies=[MockStrategy()],
            optimizer=OptimizationChain(),
            config=config
        )
        gcode_service = GCodeGenerationService(generator)
        gcode = gcode_service.generate(paths, svg_attr)
        # Buscar los índices de los comandos CMD_DOWN y CMD_UP
        down_indices = [i for i, line in enumerate(gcode) if config.cmd_down in line or 'M3 S255' in line or 'M3 S1000' in line]
        up_indices = [i for i, line in enumerate(gcode) if config.cmd_up in line or 'M5' in line]
        # Debe haber al menos un par CMD_DOWN/CMD_UP
        self.assertGreaterEqual(len(down_indices), 1)
        self.assertGreaterEqual(len(up_indices), 1)
        # Verificar que entre cada par CMD_DOWN/CMD_UP haya al menos un G1
        for d in down_indices:
            u = next((i for i in up_indices if i > d), None)
            if u is not None:
                lines_between = gcode[d+1:u]
                self.assertTrue(any(line.startswith("G1") for line in lines_between), f"No hay comando G1 entre CMD_DOWN y CMD_UP: {lines_between}")
        # Verificar que entre CMD_UP y el siguiente CMD_DOWN haya un G0
        for u in up_indices:
            # Buscar el siguiente CMD_DOWN después de este CMD_UP
            d = next((i for i in down_indices if i > u), None)
            if d is not None:
                has_g0 = any(line.startswith("G0") for line in gcode[u:d])
                self.assertTrue(has_g0, "Falta G0 entre CMD_UP y CMD_DOWN")

if __name__ == "__main__":
    unittest.main()

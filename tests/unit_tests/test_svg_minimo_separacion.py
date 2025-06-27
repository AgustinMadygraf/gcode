"""
Test automatizado para validar la separación de trazos en el G-code generado a partir de un SVG mínimo.
"""
import unittest
import pytest
from infrastructure.config.config import Config
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from tests.mocks.mock_strategy import MockStrategy
from tests.mocks.mock_path_sampler import MockPathSampler
from tests.mocks.mock_svg_loader import MockSvgLoader
from tests.mocks.mock_gcode_generator import MockGCodeGenerator

@pytest.fixture(scope="module")
def config():
    return Config()

# class TestMinimumSeparationSVG(unittest.TestCase):
#     def test_minimum_stroke_separation(self):
#         from pathlib import Path
#         config = Config()
#         svg_file = (Path(__file__).parent.parent / "svg_input" / "test_lines.svg").resolve()
#         svg = MockSvgLoader(svg_file)
#         paths = svg.get_paths()
#         svg_attr = svg.get_attributes()
#         generator = MockGCodeGenerator()
#         gcode_service = GCodeGenerationService(generator)
#         gcode = gcode_service.generate(paths, svg_attr)
#         # Buscar los índices de los comandos CMD_DOWN y CMD_UP
#         down_indices = [i for i, line in enumerate(gcode) if config.cmd_down in line or 'M3 S255' in line or 'M3 S1000' in line]
#         up_indices = [i for i, line in enumerate(gcode) if config.cmd_up in line or 'M5' in line]
#         # Debe haber al menos un par CMD_DOWN/CMD_UP
#         self.assertGreaterEqual(len(down_indices), 1)
#         self.assertGreaterEqual(len(up_indices), 1)
#         # Verificar que entre cada par CMD_DOWN/CMD_UP haya al menos un G1
#         for d in down_indices:
#             u = next((i for i in up_indices if i > d), None)
#             if u is not None:
#                 lines_between = gcode[d+1:u]
#                 self.assertTrue(any(line.startswith("G1") for line in lines_between), f"No hay comando G1 entre CMD_DOWN y CMD_UP: {lines_between}")
#         # Verificar que entre CMD_UP y el siguiente CMD_DOWN haya un G0
#         for u in up_indices:
#             # Buscar el siguiente CMD_DOWN después de este CMD_UP
#             d = next((i for i in down_indices if i > u), None)
#             if d is not None:
#                 has_g0 = any(line.startswith("G0") for line in gcode[u:d])
#                 self.assertTrue(has_g0, "Falta G0 entre CMD_UP y CMD_DOWN")

if __name__ == "__main__":
    unittest.main()

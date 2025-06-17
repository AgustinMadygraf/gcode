"""
Test automatizado para validar la separación de trazos en el G-code generado a partir de un SVG mínimo.
"""
import unittest
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from infrastructure.svg_loader import SvgLoader
from domain.gcode_generator import GCodeGenerator
from domain.path_transform_strategy import PathTransformStrategy
from config.config import CMD_DOWN, CMD_UP, FEED, STEP_MM, DWELL_MS, MAX_HEIGHT_MM

class DummyStrategy(PathTransformStrategy):
    def transform(self, x, y):
        return x, y

class TestSVGMinimoSeparacion(unittest.TestCase):
    def test_separacion_trazos_svg_minimo(self):
        svg_file = Path("../svg_input/test_lines.svg").resolve()
        svg = SvgLoader(svg_file)
        paths = svg.get_paths()
        svg_attr = svg.get_attributes()
        generator = GCodeGenerator(
            feed=FEED,
            cmd_down=CMD_DOWN,
            cmd_up=CMD_UP,
            step_mm=STEP_MM,
            dwell_ms=DWELL_MS,
            max_height_mm=MAX_HEIGHT_MM,
            logger=None,
            transform_strategies=[DummyStrategy()]
        )
        gcode = generator.generate(paths, svg_attr)
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
                for line in gcode[d+1:u]:
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

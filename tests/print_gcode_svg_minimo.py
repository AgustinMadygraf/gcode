import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from infrastructure.svg_loader import SvgLoader
from infrastructure.adapters.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.path_transform_strategy import PathTransformStrategy
from config.config import CMD_DOWN, CMD_UP, FEED, STEP_MM, DWELL_MS, MAX_HEIGHT_MM
from application.generation.optimizer_factory import make_optimization_chain

class DummyStrategy(PathTransformStrategy):
    def transform(self, x, y):
        return x, y

svg_file = Path("../svg_input/test_lines.svg").resolve()
svg = SvgLoader(svg_file)
paths = svg.get_paths()
svg_attr = svg.get_attributes()
generator = GCodeGeneratorAdapter(
    feed=FEED,
    cmd_down=CMD_DOWN,
    cmd_up=CMD_UP,
    step_mm=STEP_MM,
    dwell_ms=DWELL_MS,
    max_height_mm=MAX_HEIGHT_MM,
    logger=None,
    transform_strategies=[DummyStrategy()],
    optimizer=make_optimization_chain()  # Inyectar la cadena de optimización
)
gcode = generator.generate(paths, svg_attr)
for i, line in enumerate(gcode):
    print(f"{i:03d}: {line}")

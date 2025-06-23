import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from infrastructure.svg_loader import SvgLoaderAdapter
from adapters.output.gcode_generator_adapter import GCodeGeneratorImpl
from domain.path_transform_strategy import PathTransformStrategy
from infrastructure.config.config import Config
from application.generation.optimizer_factory import make_optimization_chain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from domain.services.optimization.optimization_chain import OptimizationChain

class MockStrategy(PathTransformStrategy):
    def transform(self, x, y):
        return x, y

config = Config()
svg_file = Path("../svg_input/test_lines.svg").resolve()
svg = SvgLoaderAdapter(svg_file)
paths = svg.get_paths()
svg_attr = svg.get_attributes()
generator = GCodeGeneratorImpl(
    feed=config.feed,
    cmd_down=config.cmd_down,
    cmd_up=config.cmd_up,
    step_mm=config.step_mm,
    dwell_ms=config.dwell_ms,
    max_height_mm=config.max_height_mm,
    logger=None,
    transform_strategies=[MockStrategy()],
    optimizer=OptimizationChain()  # Inyectar la cadena de optimización
)
gcode_service = GCodeGenerationService(generator)
gcode = gcode_service.generate(paths, svg_attr)
for i, line in enumerate(gcode):
    print(f"{i:03d}: {line}")

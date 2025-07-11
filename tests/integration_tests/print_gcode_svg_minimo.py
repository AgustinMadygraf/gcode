class DummyI18n:
    def get(self, key, **kwargs):
        return key
class DummyLogger:
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass

import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.input.svg_loader_adapter import SvgLoaderAdapter
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from infrastructure.config.config import Config
from application.generation.optimizer_factory import make_optimization_chain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from domain.services.optimization.optimization_chain import OptimizationChain
from tests.mocks.mock_strategy import MockStrategy

config = Config()
svg_file = Path("../svg_input/test_lines.svg").resolve()
svg = SvgLoaderAdapter(svg_file)
paths = svg.get_paths()
svg_attr = svg.get_attributes()
generator = GCodeGeneratorAdapter(
    path_sampler=None,  # Ajusta si tienes un path_sampler adecuado
    feed=config.feed,
    cmd_down=config.cmd_down,
    cmd_up=config.cmd_up,
    step_mm=config.step_mm,
    dwell_ms=config.dwell_ms,
    max_height_mm=config.plotter_max_area_mm[1],
    logger=DummyLogger(),
    i18n=DummyI18n(),
    transform_strategies=[MockStrategy()],
    optimizer=OptimizationChain(),
    config=config  # Asegura que config esté presente
)
gcode_service = GCodeGenerationService(generator)
gcode = gcode_service.generate(paths, svg_attr)
for i, line in enumerate(gcode):
    print(f"{i:03d}: {line}")

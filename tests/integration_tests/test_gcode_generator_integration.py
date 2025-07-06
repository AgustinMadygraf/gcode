"""
Integration test for GCodeGenerator with PathSampler and TransformManager.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.services.optimization.optimization_chain import OptimizationChain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from adapters.input.path_sampler import PathSampler
from tests.mocks.mock_geometry import DummySegment
from tests.mocks.mock_strategy import DummyStrategy
from tests.mocks.mock_config import DummyConfig

class DummyLogger:
    def info(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass
    def warning(self, *a, **k): pass

class DummyI18n:
    def get(self, key, **_kwargs):
        return key
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass

class TestGCodeGeneratorIntegration(unittest.TestCase):
    def test_generate_with_transform_manager(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            seg = DummySegment(start=(0,0), end=(10,0))
            paths = [[seg]]
            svg_attr = {"viewBox": "0 0 10 10", "width": "10"}
            generator = GCodeGeneratorAdapter(
                path_sampler=PathSampler(1),
                feed=1000,
                cmd_down="M3 S1000",
                cmd_up="M5",
                step_mm=1,
                dwell_ms=100,
                max_height_mm=10,
                logger=DummyLogger(),
                i18n=DummyI18n(),
                transform_strategies=[DummyStrategy()],
                optimizer=OptimizationChain(),
                config=DummyConfig(tmpdir)  # Mock config
            )
            gcode_service = GCodeGenerationService(generator)
            gcode = gcode_service.generate(paths, svg_attr)
            # Validar solo la línea final transformada
            self.assertIn("G1 X11.000 Y2.000 F1000", gcode)

if __name__ == "__main__":
    unittest.main()

"""
Integration test for GCodeGenerator with PathSampler and TransformManager.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.path_transform_strategy import PathTransformStrategy
from domain.services.optimization.optimization_chain import OptimizationChain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from adapters.input.path_sampler import PathSampler

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
        return x + 1, y + 2

class DummyConfig:
    def __getattr__(self, name):
        return None
    def get(self, name, default=None):
        return default

class TestGCodeGeneratorIntegration(unittest.TestCase):
    def test_generate_with_transform_manager(self):
        seg = DummySegment(10, (0,0), (10,0))
        paths = [[seg]]
        svg_attr = {"viewBox": "0 0 10 10", "width": "10"}
        generator = GCodeGeneratorAdapter(
            path_sampler=PathSampler(5),
            feed=1000,
            cmd_down="M3 S1000",
            cmd_up="M5",
            step_mm=5,
            dwell_ms=100,
            max_height_mm=10,
            logger=None,
            transform_strategies=[DummyStrategy()],
            optimizer=OptimizationChain(),
            config=DummyConfig()  # Mock config
        )
        gcode_service = GCodeGenerationService(generator)
        gcode = gcode_service.generate(paths, svg_attr)
        self.assertIn("G1 X6.000 Y2.000 F1000", gcode)
        self.assertIn("G1 X11.000 Y2.000 F1000", gcode)

if __name__ == "__main__":
    unittest.main()

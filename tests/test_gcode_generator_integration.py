"""
Integration test for GCodeGenerator with PathSampler and TransformManager.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from infrastructure.adapters.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.path_transform_strategy import PathTransformStrategy
from application.generation.optimizer_factory import make_optimization_chain

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

class TestGCodeGeneratorIntegration(unittest.TestCase):
    def test_generate_with_transform_manager(self):
        seg = DummySegment(10, (0,0), (10,0))
        paths = [[seg]]
        svg_attr = {"viewBox": "0 0 10 10", "width": "10"}
        generator = GCodeGeneratorAdapter(
            feed=1000,
            cmd_down="M3 S1000",
            cmd_up="M5",
            step_mm=5,
            dwell_ms=100,
            max_height_mm=10,
            logger=None,
            transform_strategies=[DummyStrategy()],
            optimizer=make_optimization_chain()  # Inyectar la cadena de optimización
        )
        gcode = generator.generate(paths, svg_attr)
        self.assertIn("G1 X6.000 Y2.000 F1000", gcode)
        self.assertIn("G1 X11.000 Y2.000 F1000", gcode)

if __name__ == "__main__":
    unittest.main()

"""
Path: tests/test_bounding_box_calculator.py

Este test ha quedado obsoleto tras migrar la lógica a domain/services/geometry.py.
Usar tests/test_geometry_service.py para probar la lógica de bounding box.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from domain.geometry.bounding_box_calculator import BoundingBoxCalculator

class DummySegment:
    def point(self, t):
        # Simula un segmento de línea de (0,0) a (10,10)
        return complex(10 * t, 10 * t)

class TestBoundingBoxCalculator(unittest.TestCase):
    def test_bbox_line(self):
        # Un solo path, una línea diagonal de (0,0) a (10,10)
        paths = [[DummySegment()]]
        bbox = BoundingBoxCalculator.get_svg_bbox(paths)
        self.assertAlmostEqual(bbox[0], 0)
        self.assertAlmostEqual(bbox[1], 10)
        self.assertAlmostEqual(bbox[2], 0)
        self.assertAlmostEqual(bbox[3], 10)
        center = BoundingBoxCalculator.get_center(bbox)
        self.assertAlmostEqual(center[0], 5)
        self.assertAlmostEqual(center[1], 5)
        dims = BoundingBoxCalculator.get_dimensions(bbox)
        self.assertAlmostEqual(dims[0], 10)
        self.assertAlmostEqual(dims[1], 10)
        area = BoundingBoxCalculator.get_area(bbox)
        self.assertAlmostEqual(area, 100)

if __name__ == "__main__":
    unittest.main()

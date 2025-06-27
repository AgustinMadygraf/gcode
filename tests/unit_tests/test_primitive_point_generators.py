"""
Unit tests for primitive_point_generators utilities (circle and ellipse).
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from domain.models import Point

import unittest
import numpy as np
from adapters.input.primitive_point_generators import generate_circle_points, generate_ellipse_points

class TestPrimitivePointGenerators(unittest.TestCase):
    def test_generate_circle_points_closed(self):
        center = complex(0, 0)
        radius = 10
        min_segment_length = 1
        points = generate_circle_points(center, radius, min_segment_length)
        # Should be closed (first == last)
        self.assertEqual(points[0], points[-1])
        # All points should be at distance ~radius from center
        for pt in points[:-1]:
            dist = np.hypot(pt.x - center.real, pt.y - center.imag)
            self.assertAlmostEqual(dist, radius, delta=0.01)
        self.assertGreaterEqual(len(points), 9)

    def test_generate_ellipse_points_closed(self):
        center = complex(0, 0)
        rx, ry = 10, 5
        phi = np.pi / 6
        min_segment_length = 1
        points = generate_ellipse_points(center, rx, ry, phi, min_segment_length)
        self.assertEqual(points[0], points[-1])
        self.assertGreaterEqual(len(points), 9)
        # Check that points are not all the same (ellipse is not degenerate)
        unique = set((round(pt.x, 3), round(pt.y, 3)) for pt in points)
        self.assertGreater(len(unique), 5)

if __name__ == "__main__":
    unittest.main()

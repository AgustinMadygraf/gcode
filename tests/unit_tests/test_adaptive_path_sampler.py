"""
Unit tests for AdaptivePathSampler (refactored version).
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from domain.models import Point
import unittest
from svgpathtools import Path, Line, Arc

# Stub para SVGPath (no existe en domain.models)
class SVGPath:
    def __init__(self, path):
        self.path = path

from adapters.input.adaptive_path_sampler import AdaptivePathSampler

class TestAdaptivePathSampler(unittest.TestCase):
    def setUp(self):
        self.sampler = AdaptivePathSampler(min_segment_length=0.5, max_segment_length=2.0, curvature_factor=1.0)

    def test_sample_line(self):
        path = Path(Line(0+0j, 10+0j))
        svg_path = SVGPath(path)
        points = self.sampler.sample(svg_path)
        self.assertEqual(points[0], Point(0, 0))
        self.assertEqual(points[-1], Point(10, 0))
        self.assertGreaterEqual(len(points), 2)

    def test_sample_arc(self):
        arc = Arc(0+0j, 10+0j, radius=5+0j, rotation=0, large_arc=False, sweep=True)
        path = Path(arc)
        svg_path = SVGPath(path)
        points = self.sampler.sample(svg_path)
        self.assertEqual(points[0], Point(0, 0))
        self.assertGreaterEqual(len(points), 2)

    def test_sample_small_segment(self):
        path = Path(Line(0+0j, 0.1+0j))
        svg_path = SVGPath(path)
        points = self.sampler.sample(svg_path)
        self.assertEqual(len(points), 2)

if __name__ == "__main__":
    unittest.main()

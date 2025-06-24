"""
Unit tests for PathSampler.
"""
import unittest
import math
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from adapters.input.path_sampler import PathSampler
from domain.entities.point import Point
from tests.mocks.mock_geometry import MockSegment

class TestPathSampler(unittest.TestCase):
    def test_single_segment(self):
        seg = MockSegment(10, (0,0), (10,0))
        sampler = PathSampler(step=2.5)
        points = list(sampler.sample([seg]))
        self.assertEqual(len(points), 5)
        self.assertEqual(points[0], Point(0,0))
        self.assertEqual(points[-1], Point(10,0))

    def test_multiple_segments(self):
        seg1 = MockSegment(5, (0,0), (5,0))
        seg2 = MockSegment(5, (5,0), (5,5))
        sampler = PathSampler(step=2.5)
        points = list(sampler.sample([seg1, seg2]))
        self.assertEqual(points[0], Point(0,0))
        self.assertEqual(points[3], Point(5,0))
        self.assertEqual(points[-1], Point(5,5))

    def test_short_segment(self):
        seg = MockSegment(1, (0,0), (1,0))
        sampler = PathSampler(step=5)
        points = list(sampler.sample([seg]))
        self.assertEqual(len(points), 2)
        self.assertEqual(points[0], Point(0,0))
        self.assertEqual(points[-1], Point(1,0))

if __name__ == "__main__":
    unittest.main()

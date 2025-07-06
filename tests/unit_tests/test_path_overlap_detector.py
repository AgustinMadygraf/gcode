"""
Tests unitarios para PathOverlapDetector
"""
import unittest
from domain.services.path_overlap_detector import PathOverlapDetector

class DummyPath:
    def __init__(self, path_id):
        self.path_id = path_id

class TestPathOverlapDetector(unittest.TestCase):
    def test_no_overlap_returns_all(self):
        detector = PathOverlapDetector(tool_diameter=0.4)
        paths = [DummyPath(1), DummyPath(2)]
        filtered = detector.filter_overlapping_paths(paths)
        self.assertEqual(filtered, paths)

    def test_empty_list(self):
        detector = PathOverlapDetector(tool_diameter=0.4)
        filtered = detector.filter_overlapping_paths([])
        self.assertEqual(filtered, [])

    # Aquí se pueden agregar más tests cuando se implemente la lógica real

if __name__ == "__main__":
    unittest.main()

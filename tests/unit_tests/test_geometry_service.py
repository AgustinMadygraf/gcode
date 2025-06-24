"""
Tests para GeometryService (capa de dominio).
"""
import unittest
from domain.services.geometry import GeometryService
from tests.mocks.mock_geometry import MockSegment

class TestGeometryService(unittest.TestCase):
    def test_bbox_line(self):
        # Creamos un segmento específico para este test
        class CustomMockSegment(MockSegment):
            def point(self, t):
                # Simula un segmento de línea de (0,0) a (10,10)
                return complex(10 * t, 10 * t)
                
        paths = [[CustomMockSegment()]]
        bbox = GeometryService._calculate_bbox(paths)
        self.assertAlmostEqual(bbox[0], 0)
        self.assertAlmostEqual(bbox[1], 10)
        self.assertAlmostEqual(bbox[2], 0)
        self.assertAlmostEqual(bbox[3], 10)
        center = GeometryService._center(bbox)
        self.assertAlmostEqual(center[0], 5)
        self.assertAlmostEqual(center[1], 5)

if __name__ == "__main__":
    unittest.main()

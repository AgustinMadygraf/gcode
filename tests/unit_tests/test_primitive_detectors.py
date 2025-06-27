"""
Tests unitarios para los detectores de primitivas geométricas.
"""
import unittest
import numpy as np
from svgpathtools import Path, Line, Arc
from domain.services.detectors.circle_detector import CircleDetector
from domain.services.detectors.rectangle_detector import RectangleDetector
from domain.services.detectors.ellipse_detector import EllipseDetector

class TestPrimitiveDetectors(unittest.TestCase):
    def test_circle_detector(self):
        # Círculo perfecto
        center = complex(0, 0)
        radius = 10
        arc1 = Arc(center + radius, radius + radius*1j, 0, False, True, center - radius)
        arc2 = Arc(center - radius, radius + radius*1j, 0, False, True, center + radius)
        path = Path(arc1, arc2)
        path.closed = True
        result = CircleDetector().try_detect_circle(path)
        self.assertIsNotNone(result)
        detected_center, detected_radius = result
        self.assertAlmostEqual(detected_center.real, center.real, places=1)
        self.assertAlmostEqual(detected_center.imag, center.imag, places=1)
        self.assertAlmostEqual(detected_radius, radius, places=1)

    def test_rectangle_detector(self):
        # Rectángulo perfecto
        corners = [complex(0,0), complex(10,0), complex(10,5), complex(0,5)]
        path = Path(Line(corners[0], corners[1]), Line(corners[1], corners[2]),
                    Line(corners[2], corners[3]), Line(corners[3], corners[0]))
        path.closed = True
        result = RectangleDetector().try_detect_rectangle(path)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 4)

    def test_ellipse_detector(self):
        # Elipse aproximada con muchos puntos y ruido
        import numpy as np
        from svgpathtools import Line
        center = complex(0, 0)
        rx, ry = 10, 5
        num_points = 40
        np.random.seed(42)
        points = [center + rx * np.cos(t) + 1j * ry * np.sin(t) + (np.random.normal(0, 0.05) + 1j * np.random.normal(0, 0.05))
                  for t in np.linspace(0, 2*np.pi, num_points, endpoint=False)]
        segments = [Line(points[i], points[(i+1)%num_points]) for i in range(num_points)]
        path = Path(*segments)
        path.closed = True
        result = EllipseDetector().try_detect_ellipse(path)
        self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()

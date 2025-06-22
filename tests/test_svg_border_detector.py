"""
Tests para SvgBorderDetector
"""
import unittest
from domain.filters.svg_border_detector import SvgBorderDetector
from svgpathtools import Line, Path

class TestSvgBorderDetector(unittest.TestCase):
    def test_detect_rectangle(self):
        # Crear un rectángulo simple: (0,0) -> (10,0) -> (10,10) -> (0,10) -> (0,0)
        rect = Path(
            Line(0+0j, 10+0j),
            Line(10+0j, 10+10j),
            Line(10+10j, 0+10j),
            Line(0+10j, 0+0j)
        )
        detector = SvgBorderDetector()
        self.assertTrue(detector.is_rectangle(rect))

    def test_non_rectangle(self):
        # Crear un triángulo: (0,0) -> (10,0) -> (5,10) -> (0,0)
        triangle = Path(
            Line(0+0j, 10+0j),
            Line(10+0j, 5+10j),
            Line(5+10j, 0+0j)
        )
        detector = SvgBorderDetector()
        self.assertFalse(detector.is_rectangle(triangle))

    def test_match_viewbox(self):
        # Crear un rectángulo que coincide con el viewBox
        rect = Path(
            Line(0+0j, 100+0j),
            Line(100+0j, 100+100j),
            Line(100+100j, 0+100j),
            Line(0+100j, 0+0j)
        )
        svg_attr = {"viewBox": "0 0 100 100"}
        detector = SvgBorderDetector()
        self.assertTrue(detector.matches_svg_bounds(rect, svg_attr))

    def test_different_from_viewbox(self):
        # Crear un rectángulo que no coincide con el viewBox
        rect = Path(
            Line(20+20j, 80+20j),
            Line(80+20j, 80+80j),
            Line(80+80j, 20+80j),
            Line(20+80j, 20+20j)
        )
        svg_attr = {"viewBox": "0 0 100 100"}
        detector = SvgBorderDetector()
        self.assertFalse(detector.matches_svg_bounds(rect, svg_attr))

if __name__ == "__main__":
    unittest.main()

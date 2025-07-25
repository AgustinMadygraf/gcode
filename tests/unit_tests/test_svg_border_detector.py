"""
Tests para SvgBorderDetector
"""
import unittest
from domain.filters.svg_border_detector import SvgBorderDetector
from svgpathtools import Line, Path
from infrastructure.factories.infra_factory import InfraFactory

class TestSvgBorderDetector(unittest.TestCase):
    def test_detect_rectangle(self):
        # Crear un rectángulo simple: (0,0) -> (10,0) -> (10,10) -> (0,10) -> (0,0)
        rect = Path(
            Line(0+0j, 10+0j),
            Line(10+0j, 10+10j),
            Line(10+10j, 0+10j),
            Line(0+10j, 0+0j)
        )
        logger = InfraFactory.get_logger()
        detector = SvgBorderDetector(logger=logger)
        self.assertTrue(detector.is_rectangle(rect))

    def test_non_rectangle(self):
        # Crear un triángulo: (0,0) -> (10,0) -> (5,10) -> (0,0)
        triangle = Path(
            Line(0+0j, 10+0j),
            Line(10+0j, 5+10j),
            Line(5+10j, 0+0j)
        )
        logger = InfraFactory.get_logger()
        detector = SvgBorderDetector(logger=logger)
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
        logger = InfraFactory.get_logger()
        detector = SvgBorderDetector(logger=logger)
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
        logger = InfraFactory.get_logger()
        detector = SvgBorderDetector(logger=logger)
        self.assertFalse(detector.matches_svg_bounds(rect, svg_attr))

    def test_tolerance_edge_case(self):
        # Rectángulo casi igual al viewBox, pero justo fuera de la tolerancia
        rect = Path(
            Line(0+0j, 100+0j),
            Line(100+0j, 100+100j),
            Line(100+100j, 0+100j),
            Line(0+100j, 0+0j)
        )
        svg_attr = {"viewBox": "0 0 100 100"}
        # Tolerancia muy estricta
        logger = InfraFactory.get_logger()
        detector = SvgBorderDetector(tolerance=0.00001, logger=logger)
        self.assertTrue(detector.matches_svg_bounds(rect, svg_attr))
        # Rectángulo desplazado apenas fuera de tolerancia
        rect2 = Path(
            Line(0.1+0j, 100.1+0j),
            Line(100.1+0j, 100.1+100j),
            Line(100.1+100j, 0.1+100j),
            Line(0.1+100j, 0.1+0j)
        )
        self.assertFalse(detector.matches_svg_bounds(rect2, svg_attr))

    def test_internal_rectangle_not_removed(self):
        # Un rectángulo interno, no borde
        rect = Path(
            Line(10+10j, 90+10j),
            Line(90+10j, 90+90j),
            Line(90+90j, 10+90j),
            Line(10+90j, 10+10j)
        )
        svg_attr = {"viewBox": "0 0 100 100"}
        logger = InfraFactory.get_logger()
        detector = SvgBorderDetector(logger=logger)
        self.assertFalse(detector.matches_svg_bounds(rect, svg_attr))

if __name__ == "__main__":
    unittest.main()

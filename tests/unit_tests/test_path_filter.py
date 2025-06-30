import unittest
from svgpathtools import Path, Line
from domain.services.path_filter_service import PathFilter
from infrastructure.factories.infra_factory import InfraFactory

class TestPathFilter(unittest.TestCase):
    def test_removes_border_but_keeps_internal_rectangle(self):
        # Path que simula el borde del SVG
        border_path = Path(Line(0+0j, 100+0j), Line(100+0j, 100+100j), Line(100+100j, 0+100j), Line(0+100j, 0+0j))
        # Path de un rectángulo interno deseado
        internal_rect = Path(Line(20+20j, 80+20j), Line(80+20j, 80+80j), Line(80+80j, 20+80j), Line(20+80j, 20+20j))
        
        paths = [border_path, internal_rect]
        svg_attr = {"viewBox": "0 0 100 100"}
        
        # Crear filtro que SÍ elimina el borde
        logger = InfraFactory.get_logger()
        path_filter = PathFilter(remove_svg_border=True, border_tolerance=0.05, logger=logger)
        
        filtered_paths = path_filter.filter_nontrivial(paths, svg_attr)
        
        self.assertEqual(len(filtered_paths), 1, "Debería quedar solo un path.")
        self.assertIs(filtered_paths[0], internal_rect, "El path restante debe ser el rectángulo interno.")

if __name__ == "__main__":
    unittest.main()

"""
Mocks para pruebas de cargadores SVG.
"""
from domain.ports.svg_loader_port import SvgLoaderPort

class MockSvgLoader(SvgLoaderPort):
    """
    Implementación simulada del cargador SVG para pruebas unitarias.
    """
    def __init__(self, svg_file):
        self.svg_file = svg_file
        
    def get_paths(self):
        """Retorna paths mockeados para el test"""
        return []  # Implementar según necesidad del test
        
    def get_attributes(self):
        """Retorna atributos mockeados"""
        return {}
        
    def load(self):
        """Simulación de carga"""
        pass  # Implementación vacía para cumplir con la interfaz

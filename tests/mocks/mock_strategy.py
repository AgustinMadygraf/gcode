"""
Mocks para pruebas de estrategias de transformación de rutas.
"""
from domain.path_transform_strategy import PathTransformStrategy

class MockStrategy(PathTransformStrategy):
    """
    Implementación simulada de estrategia de transformación para pruebas unitarias.
    """
    def transform(self, x, y):
        """Implementación de identidad para pruebas"""
        return x, y

class DummyStrategy(PathTransformStrategy):
    """
    Estrategia de transformación simulada que suma valores constantes a las coordenadas.
    """
    def __init__(self, x_offset=1, y_offset=2):
        self.x_offset = x_offset
        self.y_offset = y_offset
        
    def transform(self, x, y):
        """Desplaza las coordenadas por una cantidad fija"""
        return x + self.x_offset, y + self.y_offset

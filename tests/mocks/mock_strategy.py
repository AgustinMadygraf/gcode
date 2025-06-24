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

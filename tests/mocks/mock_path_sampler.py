"""
Mocks para pruebas de muestreo de rutas.
"""
from domain.ports.path_sampler_port import PathSamplerPort
from domain.entities.point import Point

class MockPathSampler(PathSamplerPort):
    """
    Implementación simulada del muestreador de rutas para pruebas unitarias.
    """
    def sample(self, path):
        """Convierte los segmentos del path en una lista de Point"""
        points = []
        for seg in path:
            # samplea 2 puntos por segmento (inicio y fin)
            z0 = seg.point(0)
            z1 = seg.point(1)
            points.append(Point(z0.real, z0.imag))
            points.append(Point(z1.real, z1.imag))
        return points

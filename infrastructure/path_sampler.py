"""
PathSampler: Utility to sample points along SVG paths at fixed intervals.

- step: distancia entre puntos muestreados (en unidades SVG)
- sample(path): recibe una lista de segmentos SVG y produce tuplas (x, y) a intervalos regulares.
- Lanza ValueError si step <= 0.

Ejemplo de uso:
    sampler = PathSampler(step=2.0)
    for x, y in sampler.sample(path):
        print(x, y)
"""
import math
import numpy as np
from domain.models import Point

class PathSampler:
    """Samples points along SVG paths at specified intervals."""
    def __init__(self, step: float, logger=None):
        if step <= 0:
            raise ValueError("step must be positive")
        self.step = step
        self.logger = logger

    def sample(self, path):
        """Yield Point objects sampled along the path at the given step interval.
        Args:
            path: Iterable de segmentos, cada uno con .length() y .point(t).
        Yields:
            Point: Coordenadas (x, y) muestreadas.
        """
        for seg in path:
            seg_len = seg.length()
            n = max(1, int(math.ceil(seg_len / self.step)))
            for t in np.linspace(0, 1, n + 1):
                z = seg.point(t)
#                if self.logger:
#                    self.logger.debug(f"Sampled point: ({z.real:.3f}, {z.imag:.3f})")
                yield Point(z.real, z.imag)

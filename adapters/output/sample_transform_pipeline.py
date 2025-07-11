"""
SampleTransformPipeline: Servicio para muestrear y transformar paths SVG en listas de puntos, aplicando escalado y transformaciones.
"""
from typing import List, Any
from domain.entities.point import Point
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.transform_manager_port import TransformManagerPort

class SampleTransformPipeline:
    " Servicio para muestrear y transformar paths SVG en listas de puntos, aplicando escalado y transformaciones. "
    def __init__(self, path_sampler: PathSamplerPort, transform_manager: TransformManagerPort, scale: float):
        self.path_sampler = path_sampler
        self.transform_manager = transform_manager
        self.scale = scale

    def process(self, paths: List[Any]) -> List[List[Point]]:
        " Procesa los paths, muestrea y transforma cada uno en una lista de puntos. "
        result = []
        for idx, p in enumerate(paths):
            if not hasattr(p, '__iter__') or isinstance(p, (str, bytes)):
                raise TypeError(f"[ERROR] Path {idx} no es iterable: {type(p)}. Se esperaba una lista de segmentos.")
            points = []
            for pt in self.path_sampler.sample(p):
                x, y = self.transform_manager.apply(pt.x, pt.y)
                x, y = x * self.scale, y * self.scale
                points.append(Point(x, y))
            result.append(points)
        return result

"""
SampleTransformPipeline: Servicio para muestrear y transformar paths SVG en listas de puntos, aplicando escalado y transformaciones.
"""
from typing import List, Any
from domain.entities.point import Point
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.transform_manager_port import TransformManagerPort

class SampleTransformPipeline:
    def __init__(self, path_sampler: PathSamplerPort, transform_manager: TransformManagerPort, scale: float):
        self.path_sampler = path_sampler
        self.transform_manager = transform_manager
        self.scale = scale

    def process(self, paths: List[Any]) -> List[List[Point]]:
        result = []
        for p in paths:
            points = []
            for pt in self.path_sampler.sample(p):
                x, y = self.transform_manager.apply(pt.x, pt.y)
                x, y = x * self.scale, y * self.scale
                points.append(Point(x, y))
            result.append(points)
        return result

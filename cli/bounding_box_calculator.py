"""
BoundingBoxCalculator: Clase utilitaria para calcular el bounding box y centro de paths SVG.
Ahora delega la lógica al servicio de dominio GeometryService.
"""
from typing import Tuple, List, Any
from domain.services.geometry import GeometryService

class BoundingBoxCalculator:
    """
    Clase utilitaria para calcular el bounding box y centro de paths SVG.
    Ahora delega la lógica al servicio de dominio GeometryService.
    """
    @staticmethod
    def calculate_bbox(paths: List[Any]) -> Tuple[float, float, float, float]:
        return GeometryService.calculate_bbox(paths)

    @staticmethod
    def center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        return GeometryService.center(bbox)

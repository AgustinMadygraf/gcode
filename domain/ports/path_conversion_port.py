"""
Puerto de conversión de paths a G-code para el dominio.
Define la interfaz que debe implementar cualquier servicio de conversión.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict

class PathConversionPort(ABC):
    """
    Interfaz para convertir paths y atributos SVG en líneas de G-code.
    """
    @abstractmethod
    def convert_paths_to_gcode(self, paths: List[Any], svg_attr: Dict[str, Any]) -> List[str]:
        """
        Convierte una lista de paths y atributos SVG en líneas de G-code.
        """
        pass

__all__ = [
    "PathConversionPort"
]

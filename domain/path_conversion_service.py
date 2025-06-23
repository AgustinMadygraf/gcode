"""
Servicio de conversión de paths a G-code en el dominio.
Define la interfaz y la responsabilidad de orquestar la conversión, sin implementación.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict

class PathConversionService(ABC):
    @abstractmethod
    def convert_paths_to_gcode(self, paths: List[Any], svg_attr: Dict[str, Any]) -> List[str]:
        """
        Convierte una lista de paths y atributos SVG en líneas de G-code.
        """
        pass

"""
Puerto SvgLoaderPort: interfaz para cargar SVGs en el dominio.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict
from domain.entities.path import Path

class SvgLoaderPort(ABC):
    """
    Interfaz para cargar archivos SVG en el dominio. 
    Proporciona métodos para cargar un archivo SVG,
    obtener las rutas y los atributos del documento SVG.
    """
    @abstractmethod
    def load(self, file_path: str) -> None:
        " Carga un archivo SVG desde la ruta especificada. """
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

    @abstractmethod
    def get_paths(self) -> List[Path]:
        " Obtiene las rutas del documento SVG cargado. "
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

    @abstractmethod
    def get_attributes(self) -> Dict[str, Any]:
        " Obtiene los atributos del documento SVG cargado. "
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

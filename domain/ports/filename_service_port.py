"""
Puerto que define las operaciones para gestión de nombres de archivo.
Siguiendo los principios de Clean Architecture, el dominio define la interfaz
pero no la implementación específica del sistema de archivos.
"""
from abc import ABC, abstractmethod
from pathlib import Path

class FilenameServicePort(ABC):
    """
    Puerto para la generación de nombres de archivos según convenciones.
    Los casos de uso dependerán de esta abstracción, no de implementaciones concretas.
    """
    @abstractmethod
    def next_filename(self, source_file: Path) -> Path:
        """
        Genera el siguiente nombre de archivo disponible según convención.
        Args:
            source_file: Archivo de origen (normalmente SVG)
        Returns:
            Path: Ruta completa al nuevo archivo a generar
        """
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

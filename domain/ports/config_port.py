"""
Puerto ConfigPort: interfaz para obtener configuración de compresión en el dominio.
"""

from abc import ABC, abstractmethod
from domain.compression_config import CompressionConfig

class ConfigPort(ABC):
    """
    Interfaz para obtener configuración de compresión desde el origen de datos.
    """

    @abstractmethod
    def get_compression_config(self) -> CompressionConfig:
        """Obtiene configuración de compresión desde el origen de datos"""
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

    @abstractmethod
    def get_debug_flag(self, name: str) -> bool:
        """Devuelve el flag de debug para un componente dado."""
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

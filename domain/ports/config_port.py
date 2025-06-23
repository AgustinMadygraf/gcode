from abc import ABC, abstractmethod
from domain.models.compression_config import CompressionConfig

class ConfigPort(ABC):
    @abstractmethod
    def get_compression_config(self) -> CompressionConfig:
        """Obtiene configuración de compresión desde el origen de datos"""
        pass

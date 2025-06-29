"""
Puerto GcodeCompressionPort: interfaz para compresión de G-code en el dominio.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from domain.compression_metrics import CompressionMetrics

class GcodeCompressionPort(ABC):
    """
    Interfaz para comprimir líneas G-code respetando una tolerancia máxima.
    """
    @abstractmethod
    def compress(self, gcode_lines: List[str], tolerance: float) -> Tuple[List[str], CompressionMetrics]:
        """Comprime líneas G-code respetando una tolerancia máxima"""
        pass

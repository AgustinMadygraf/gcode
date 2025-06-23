from abc import ABC, abstractmethod
from typing import List, Tuple
from domain.models.compression_metrics import CompressionMetrics

class GcodeCompressionPort(ABC):
    @abstractmethod
    def compress(self, gcode_lines: List[str], tolerance: float) -> Tuple[List[str], CompressionMetrics]:
        """Comprime líneas G-code respetando una tolerancia máxima"""
        pass

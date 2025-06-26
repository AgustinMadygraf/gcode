# Servicio de aplicación para compresión de G-code
# (Movido desde domain/gcode_compression_service.py)
from typing import List, Tuple
from domain.ports.gcode_compression_port import GcodeCompressionPort
from domain.models.compression_metrics import CompressionMetrics
from domain.models.compression_config import CompressionConfig
from domain.services.validation.gcode_validator import GCodeValidator

class GcodeCompressionService:
    """Servicio de aplicación para comprimir G-code con múltiples estrategias"""

    def __init__(self, compressors: List[GcodeCompressionPort], logger=None):
        self.compressors = compressors
        self.logger = logger

    def compress(self, gcode_lines: List[str], config: CompressionConfig) -> Tuple[List[str], CompressionMetrics]:
        """Aplica compresión según la configuración proporcionada"""
        # Validar integridad G-code antes de procesar
        valido, error = GCodeValidator.validate(gcode_lines)
        if not valido:
            if self.logger:
                self.logger.error(f"Validación G-code fallida: {error}")
            raise ValueError(f"Archivo G-code inválido: {error}")

        if not config.enabled or not self.compressors:
            return gcode_lines, CompressionMetrics(
                original_lines=len(gcode_lines),
                compressed_lines=len(gcode_lines)
            )

        compressed = gcode_lines
        metrics = CompressionMetrics(
            original_lines=len(gcode_lines),
            compressed_lines=len(gcode_lines)
        )

        for compressor in self.compressors:
            compressed, comp_metrics = compressor.compress(compressed, config.geometric_tolerance)
            metrics.compressed_lines = comp_metrics.compressed_lines
            metrics.arcs_created += comp_metrics.arcs_created
            metrics.relative_moves += comp_metrics.relative_moves
            metrics.redundancies_removed += comp_metrics.redundancies_removed
            if self.logger:
                self.logger.info(f"Compresión {compressor.__class__.__name__}: {comp_metrics.percentage_saved:.2f}%")

        return compressed, metrics

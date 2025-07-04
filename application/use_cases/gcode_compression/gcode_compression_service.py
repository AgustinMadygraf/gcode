# Servicio de aplicación para compresión de G-code
# (Movido desde domain/gcode_compression_service.py)
from typing import List, Tuple
from domain.ports.gcode_compression_port import GcodeCompressionPort
from domain.compression_metrics import CompressionMetrics
from domain.compression_config import CompressionConfig
from domain.services.validation.gcode_validator import GCodeValidator

class GcodeCompressionService:
    """Servicio de aplicación para comprimir G-code con múltiples estrategias"""

    def __init__(self, compressors: List[GcodeCompressionPort], logger=None):
        self.compressors = compressors
        self.logger = logger

    def compress(self, gcode_lines: List[str], config: CompressionConfig) -> Tuple[List[str], CompressionMetrics]:
        """Aplica compresión según la configuración proporcionada"""
        if self.logger:
            self.logger.info(f"[GCODE-COMPRESSION] Inicio de compresión. Líneas originales: {len(gcode_lines)}. Config: enabled={config.enabled}, tolerancia={getattr(config, 'geometric_tolerance', None)}")
        # Validar integridad G-code antes de procesar
        valido, error = GCodeValidator.validate(gcode_lines)
        if not valido:
            if self.logger:
                self.logger.error(f"Validación G-code fallida: {error}")
            raise ValueError(f"Archivo G-code inválido: {error}")

        if not config.enabled:
            if self.logger:
                self.logger.info("Compresión deshabilitada por configuración.")
            return gcode_lines, CompressionMetrics(
                original_lines=len(gcode_lines),
                compressed_lines=len(gcode_lines)
            )
        if not self.compressors:
            if self.logger:
                self.logger.info("No hay compresores activos. Se omite compresión.")
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
            if self.logger:
                self.logger.debug(f"Ejecutando compresor: {compressor.__class__.__name__}")
            compressed, comp_metrics = compressor.compress(compressed, config.geometric_tolerance)
            metrics.compressed_lines = comp_metrics.compressed_lines
            metrics.arcs_created += comp_metrics.arcs_created
            metrics.relative_moves += comp_metrics.relative_moves
            metrics.redundancies_removed += comp_metrics.redundancies_removed
            if self.logger:
                self.logger.info(f"Compresión {compressor.__class__.__name__}: {comp_metrics.percentage_saved:.2f}%")
                self.logger.debug(f"Métricas: {comp_metrics}")

        # Advertir si la compresión fue poco efectiva
        if self.logger and metrics.original_lines > 0:
            reduction = 1 - (metrics.compressed_lines / metrics.original_lines)
            if reduction < 0.05:
                self.logger.warning(f"Compresión poco efectiva: solo {reduction*100:.2f}% de reducción.")

        if self.logger:
            self.logger.info(f"[GCODE-COMPRESSION] Fin de compresión. Líneas finales: {metrics.compressed_lines}")
        return compressed, metrics

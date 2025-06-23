from domain.ports.gcode_compression_port import GcodeCompressionPort
from domain.models.compression_metrics import CompressionMetrics
from typing import List, Tuple

class ArcCompressor(GcodeCompressionPort):
    """Comprime secuencias de movimientos lineales en arcos G2/G3"""

    def compress(self, gcode_lines: List[str], tolerance: float) -> Tuple[List[str], CompressionMetrics]:
        from infrastructure.optimizers.arc_optimizer import ArcOptimizer
        optimizer = ArcOptimizer(tolerance=tolerance)
        # ArcOptimizer espera comandos, no líneas de texto. Aquí solo devolvemos los originales y métricas vacías.
        # TODO: Implementar conversión de líneas G-code a comandos si se desea compresión real.
        metrics = CompressionMetrics(
            original_lines=len(gcode_lines),
            compressed_lines=len(gcode_lines),
            arcs_created=0,
            relative_moves=0,
            redundancies_removed=0
        )
        return gcode_lines, metrics

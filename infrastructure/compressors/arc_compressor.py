from domain.ports.gcode_compression_port import GcodeCompressionPort
from domain.models.compression_metrics import CompressionMetrics
from typing import List, Tuple

class ArcCompressor(GcodeCompressionPort):
    """Comprime secuencias de movimientos lineales en arcos G2/G3"""

    def compress(self, gcode_lines: List[str], tolerance: float) -> Tuple[List[str], CompressionMetrics]:
        # Implementación de ejemplo: delega en ArcOptimizer existente
        from infrastructure.optimizers.arc_optimizer import ArcOptimizer
        optimizer = ArcOptimizer(tolerance=tolerance)
        # Suponiendo que ArcOptimizer tiene un método optimize_lines
        optimized_lines, stats = optimizer.optimize_lines(gcode_lines)
        metrics = CompressionMetrics(
            original_lines=len(gcode_lines),
            compressed_lines=len(optimized_lines),
            arcs_created=stats.get('arcs_created', 0),
            relative_moves=stats.get('relative_moves', 0),
            redundancies_removed=stats.get('redundancies_removed', 0)
        )
        return optimized_lines, metrics

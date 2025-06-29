from dataclasses import dataclass

@dataclass
class CompressionMetrics:
    """Métricas de resultado de compresión"""
    original_lines: int
    compressed_lines: int
    arcs_created: int = 0
    relative_moves: int = 0
    redundancies_removed: int = 0

    @property
    def percentage_saved(self) -> float:
        """Porcentaje de reducción logrado"""
        if self.original_lines == 0:
            return 0.0
        return ((self.original_lines - self.compressed_lines) / self.original_lines) * 100.0

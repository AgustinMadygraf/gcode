from dataclasses import dataclass

@dataclass
class CompressionConfig:
    """Modelo de dominio para configuración de compresión"""
    enabled: bool = True
    geometric_tolerance: float = 0.1
    use_arcs: bool = True
    use_relative_moves: bool = False
    remove_redundancies: bool = True

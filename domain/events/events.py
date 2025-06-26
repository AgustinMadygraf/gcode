"""
Definición de eventos tipados para el sistema de eventos de la aplicación.
"""
from dataclasses import dataclass
from typing import Any, Dict

class Event:
    """Clase base para todos los eventos."""
    pass

@dataclass
class GcodeGeneratedEvent(Event):
    output_file: str
    lines: int
    metadata: Dict[str, Any] = None

@dataclass
class GcodeRescaledEvent(Event):
    output_file: str
    original_dimensions: Dict[str, float]
    new_dimensions: Dict[str, float]
    scale_factor: float
    commands_rescaled: Dict[str, int]

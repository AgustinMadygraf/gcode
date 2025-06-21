"""
Entidad Path: representa un conjunto de segmentos conectados.
"""
from dataclasses import dataclass
from typing import List
from domain.entities.segment import Segment

@dataclass
class Path:
    " Representa un camino formado por segmentos conectados."
    segments: List[Segment]

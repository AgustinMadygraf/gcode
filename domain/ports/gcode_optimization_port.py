"""
Puerto GcodeOptimizationPort: interfaz para optimización de comandos G-code en el dominio.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.gcode.commands.base_command import BaseCommand

class GcodeOptimizationPort(ABC):
    """
    Interfaz para optimizar comandos G-code y retornar métricas de optimización.
    """
    @abstractmethod
    def optimize(self, commands: List[BaseCommand], tolerance: float) -> tuple[List[BaseCommand], Dict[str, Any]]:
        """Optimiza comandos y retorna métricas de optimización"""
        pass

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from domain.gcode.commands.base_command import BaseCommand

"""
Puerto GcodeOptimizationChainPort: interfaz para cadena de optimización de comandos G-code en el dominio.
"""

class GcodeOptimizationChainPort(ABC):
    """
    Interfaz para ejecutar una cadena de optimizaciones sobre comandos G-code.
    """

    @abstractmethod
    def optimize(self, commands: List[BaseCommand]) -> Tuple[List[BaseCommand], Dict[str, Any]]:
        """Ejecuta una cadena de optimizaciones y retorna comandos optimizados junto con métricas"""
        pass

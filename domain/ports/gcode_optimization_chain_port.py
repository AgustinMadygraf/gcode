from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from domain.gcode.commands.base_command import BaseCommand

class GcodeOptimizationChainPort(ABC):
    @abstractmethod
    def optimize(self, commands: List[BaseCommand]) -> Tuple[List[BaseCommand], Dict[str, Any]]:
        """Ejecuta una cadena de optimizaciones y retorna comandos optimizados junto con métricas"""
        pass

"""
GCodeOptimizer: Interfaz para optimizadores de comandos G-code (Chain of Responsibility).
"""
from abc import ABC, abstractmethod
from typing import List
from domain.gcode.commands.base_command import BaseCommand
from domain.ports.gcode_optimization_port import GcodeOptimizationPort

class GCodeOptimizer(ABC):
    def __init__(self):
        self._next = None

    def set_next(self, next_optimizer: 'GCodeOptimizer') -> 'GCodeOptimizer':
        self._next = next_optimizer
        return next_optimizer

    @abstractmethod
    def optimize(self, commands: List[BaseCommand]) -> List[BaseCommand]:
        pass

    def _call_next(self, commands: List[BaseCommand]) -> List[BaseCommand]:
        if self._next:
            return self._next.optimize(commands)
        return commands

# Las implementaciones concretas de optimizadores han sido migradas a infrastructure/optimizers/

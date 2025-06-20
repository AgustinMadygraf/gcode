"""
BaseFormatter: Interfaz base para formateadores de comandos G-code.
"""
from abc import ABC, abstractmethod
from domain.gcode.commands.base_command import BaseCommand

class BaseFormatter(ABC):
    @abstractmethod
    def format_command(self, command: BaseCommand) -> str:
        """Devuelve la línea de G-code formateada para un comando."""
        pass

"""
BaseCommand: Interfaz base para comandos G-code.
"""
from abc import ABC, abstractmethod

class BaseCommand(ABC):
    @abstractmethod
    def to_gcode(self) -> str:
        """Devuelve la representación en G-code del comando."""
        pass

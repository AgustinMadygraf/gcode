"""
Interfaz base para estrategias de modo de ejecución (interactivo/no interactivo).
"""
from abc import ABC, abstractmethod

class ModeStrategy(ABC):
    @abstractmethod
    def run(self, app):
        pass

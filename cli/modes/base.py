"""
Interfaz base para estrategias de modo de ejecución (interactivo/no interactivo).
"""
from abc import ABC, abstractmethod

class ModeStrategy(ABC):
    " Interfaz base para estrategias de modo de ejecución (interactivo/no interactivo)."
    @abstractmethod
    def run(self, app):
        " Método abstracto para ejecutar la estrategia de modo."
        pass # noqa: W0107  # pylint: disable=unnecessary-pass

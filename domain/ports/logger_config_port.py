"""
Puerto para configuración de logging (nivel, color, stream, etc).
Permite desacoplar la infraestructura de la configuración concreta del logger.
"""
from abc import ABC, abstractmethod

class LoggerConfigPort(ABC):
    @abstractmethod
    def get_logger(self, use_color: bool = True, level: str = 'INFO', stream=None):
        """
        Devuelve una instancia de logger configurada según los parámetros.
        """
        pass

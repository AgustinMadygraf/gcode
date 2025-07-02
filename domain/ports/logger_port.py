"""
Path: domain/ports/logger_port.py
Puerto de logger para Clean Architecture.
Define la interfaz mínima para logging desacoplado.
"""
from abc import ABC, abstractmethod

class LoggerPort(ABC):
    @abstractmethod
    def debug(self, msg: str, *args, **kwargs):
        pass

    @abstractmethod
    def info(self, msg: str, *args, **kwargs):
        pass

    @abstractmethod
    def warning(self, msg: str, *args, **kwargs):
        pass

    @abstractmethod
    def error(self, msg: str, *args, **kwargs):
        pass

    @abstractmethod
    def exception(self, msg: str, *args, **kwargs):
        pass

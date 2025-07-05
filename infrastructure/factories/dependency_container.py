"""
Contenedor de dependencias para Clean Architecture.
Permite propagar el logger y otras dependencias de forma centralizada.
"""
from domain.ports.logger_port import LoggerPort

class DependencyContainer:
    def __init__(self, logger: LoggerPort = None, **services):
        self._logger = logger
        self._services = dict(services)
        if logger:
            self._services['logger'] = logger

    def get(self, key: str):
        return self._services.get(key)

    @property
    def logger(self):
        return self._logger


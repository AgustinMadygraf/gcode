"""
Logger adapter for Clean Architecture.
Implements LoggerPort using Python's standard logging.
"""
import logging
from domain.ports.logger_port import LoggerPort

class LoggerAdapter(LoggerPort):
    def __init__(self, name="svg2gcode", level=logging.INFO):
        self._logger = logging.getLogger(name)

        self._logger.setLevel(level)
    def debug(self, msg, *a, **kw): self._logger.debug(msg, *a, **kw)

    def info (self, msg, *a, **kw): self._logger.info (msg, *a, **kw)

    def warning(self, msg, *a, **kw): self._logger.warning(msg, *a, **kw)

    def error  (self, msg, *a, **kw): self._logger.error  (msg, *a, **kw)

    def exception(self, msg, *a, **kw): self._logger.exception(msg, *a, **kw)

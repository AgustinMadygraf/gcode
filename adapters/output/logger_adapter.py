"""
Logger adapter for Clean Architecture.
Implements LoggerPort using Python's standard logging.
"""
import logging
from domain.ports.logger_port import LoggerPort

class LoggerAdapter(LoggerPort):
    def __init__(self, name="svg2gcode"):
        self._logger = logging.getLogger(name)

    def debug(self, msg, *args, **kwargs):
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._logger.exception(msg, *args, **kwargs)

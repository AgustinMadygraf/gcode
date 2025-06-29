"""
Factory para infraestructura (configuración, logger, etc).
"""
from pathlib import Path
from infrastructure.config.config import Config
from domain.ports.logger_config_port import LoggerConfigPort
from infrastructure.logger import ConsoleLogger

class LoggerConfigAdapter(LoggerConfigPort):
    def get_logger(self, use_color: bool = True, level: str = 'INFO', stream=None):
        return ConsoleLogger(use_color=use_color, level=level, stream=stream)

class InfraFactory:
    @staticmethod
    def create_config(config_path="infrastructure/config/config.json"):
        return Config(Path(config_path))

    @staticmethod
    def get_logger(use_color=True, level='INFO', stream=None):
        # Permite crear loggers configurables
        return LoggerConfigAdapter().get_logger(use_color=use_color, level=level, stream=stream)

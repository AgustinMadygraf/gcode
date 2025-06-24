"""
Factory para infraestructura (configuración, logger, etc).
"""
from pathlib import Path
from infrastructure.config.config import Config
from infrastructure.logger import logger

class InfraFactory:
    @staticmethod
    def create_config(config_path="infrastructure/config/config.json"):
        return Config(Path(config_path))

    @staticmethod
    def get_logger():
        return logger

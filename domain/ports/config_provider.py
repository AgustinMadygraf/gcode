"""
config_provider.py: Interfaz para acceso a configuración desde capas superiores
"""
from abc import ABC, abstractmethod
from pathlib import Path

class ConfigProviderPort(ABC):
    @abstractmethod
    def get_svg_input_dir(self) -> Path:
        pass

    @abstractmethod
    def get_gcode_output_dir(self) -> Path:
        pass

    @abstractmethod
    def get_remove_svg_border(self) -> bool:
        pass

    @abstractmethod
    def get_border_detection_tolerance(self) -> float:
        pass

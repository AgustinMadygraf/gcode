"""
Puerto GcodeGeneratorPort: interfaz para generación de G-code en el dominio.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict
from domain.entities.path import Path

class GcodeGeneratorPort(ABC):
    @abstractmethod
    def generate(self, paths: List[Path], svg_attr: Dict[str, Any]) -> List[str]:
        pass

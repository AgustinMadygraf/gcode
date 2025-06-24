"""
Puerto: PathFilterPort
Define la interfaz para el filtrado de paths SVG.
"""
from typing import List, Any
from abc import ABC, abstractmethod

class PathFilterPort(ABC):
    @abstractmethod
    def filter_nontrivial(self, paths: List[Any], svg_attr: dict = None) -> List[Any]:
        """
        Filtra paths según criterios configurables.
        """
        pass

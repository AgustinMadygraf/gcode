from abc import ABC, abstractmethod
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort

"""
Puerto GcodeOptimizationFactoryPort: interfaz para crear cadenas de optimización en el dominio.
"""

class GcodeOptimizationFactoryPort(ABC):
    """
    Interfaz para crear y retornar una cadena de optimización de G-code.
    """
    @abstractmethod
    def create_optimization_chain(self) -> GcodeOptimizationChainPort:
        """Crea y retorna una cadena de optimización"""
        pass

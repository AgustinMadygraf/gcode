from abc import ABC, abstractmethod
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort

class GcodeOptimizationFactoryPort(ABC):
    @abstractmethod
    def create_optimization_chain(self) -> GcodeOptimizationChainPort:
        """Crea y retorna una cadena de optimización"""
        pass

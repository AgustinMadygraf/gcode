"""
Implementación de orquestación de conversión de paths a G-code.
Depende del puerto de dominio y orquesta la lógica de conversión.
"""
from domain.ports.path_conversion_port import PathConversionPort
from typing import Any, List, Dict

class PathConversionService(PathConversionPort):
    def convert_paths_to_gcode(self, paths: List[Any], svg_attr: Dict[str, Any]) -> List[str]:
        # Aquí iría la lógica de orquestación, llamando a reglas de dominio y adaptadores
        # Por ahora, solo un stub
        raise NotImplementedError("Implementar la lógica de conversión en Application/UseCases")

__all__ = [
    "PathConversionService"
]

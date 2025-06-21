"""
Entidad SVGDocument: representa un documento SVG en el dominio.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from domain.entities.path import Path

@dataclass
class SVGDocument:
    " Representa un documento SVG con múltiples caminos y atributos. "
    paths: List[Path]
    attributes: Dict[str, Any]

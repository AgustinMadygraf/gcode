"""
ISvgLoader: Interfaz base para loaders de SVG.
Permite testeo y mocks.
"""
from typing import List, Any, Dict, Tuple
from pathlib import Path

class ISvgLoader:
    " Interfaz base para loaders de SVG. Permite testeo y mocks. "
    def __init__(self, svg_file: Path):
        pass

    def load_paths(self) -> List[Any]:
        """Carga y devuelve los paths SVG."""
        raise NotImplementedError

    def load_attributes(self) -> Dict:
        """Carga y devuelve los atributos del SVG."""
        raise NotImplementedError

    def get_viewbox(self) -> Tuple[float, float, float, float]:
        """Devuelve el viewBox del SVG como una tupla (x, y, width, height)."""
        raise NotImplementedError

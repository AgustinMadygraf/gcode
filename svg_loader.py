"""
Path: svg_loader.py
"""
from pathlib import Path
from typing import Any, List, Tuple
from svgpathtools import svg2paths2, Path as SvgPath

class SvgLoader:
    """
    Clase para cargar y extraer paths y atributos de un archivo SVG.
    """
    def __init__(self, svg_file: Path):
        self.svg_file = svg_file
        self.paths: List[SvgPath] = []
        self.attributes: dict[str, Any] = {}
        self._load()

    def _load(self):
        paths, _, attr = svg2paths2(str(self.svg_file))
        self.paths = paths
        self.attributes = attr

    def get_paths(self) -> List[SvgPath]:
        " Devuelve una lista de paths SVG cargados. "
        return self.paths

    def get_attributes(self) -> dict:
        " Devuelve los atributos del SVG. "
        return self.attributes

    def get_viewbox(self) -> Tuple[float, float, float, float]:
        " Devuelve el viewBox del SVG como una tupla (x, y, width, height). "
        vb = self.attributes.get("viewBox")
        if vb:
            return tuple(map(float, vb.split()))
        raise ValueError("El SVG no tiene viewBox declarado.")

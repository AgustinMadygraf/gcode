"""
Path: adapters/input/svg_loader_adapter.py
"""
from pathlib import Path
from typing import Any, List, Tuple
from svgpathtools import svg2paths2, Path as SvgPath
from domain.ports.svg_loader_port import SvgLoaderPort

class SvgLoaderAdapter(SvgLoaderPort):
    """
    Clase para cargar y extraer paths y atributos de un archivo SVG.
    """
    def __init__(self, svg_file: Path):
        super().__init__()
        self.svg_file = svg_file
        self.paths: List[SvgPath] = []
        self.attributes: dict[str, Any] = {}
        self._paths_loaded = False
        self._attributes_loaded = False
        self._load()

    def _load(self):
        paths, _, attr = svg2paths2(str(self.svg_file))
        self.paths = paths
        self.attributes = attr
        self._paths_loaded = True
        self._attributes_loaded = True

    def load_paths(self) -> List[SvgPath]:
        """Carga y devuelve los paths SVG."""
        if not self._paths_loaded:
            self._load()
        return self.paths

    def load_attributes(self) -> dict:
        """Carga y devuelve los atributos del SVG."""
        if not self._attributes_loaded:
            self._load()
        return self.attributes

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

    def get_subpaths(self) -> List[SvgPath]:
        """
        Devuelve una lista de sub-paths simples a partir de los paths cargados.
        Preserva la continuidad de los paths y solo divide cuando hay una discontinuidad real.
        Una discontinuidad se detecta si la distancia entre el final de un segmento y el inicio del siguiente
        es mayor a una tolerancia.
        """
        # Implementación pendiente o migrada según necesidades del dominio
        return self.paths

    def load(self, file_path: str) -> None:
        """Implementación requerida por SvgLoaderPort. Carga el archivo SVG indicado."""
        self.svg_file = Path(file_path)
        self._load()
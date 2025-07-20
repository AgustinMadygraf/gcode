"""
Path: adapters/input/svg_loader_adapter.py
"""
from pathlib import Path
from typing import Any, List
from svgpathtools import svg2paths2, Path as SvgPath
from svgpathtools import Line, QuadraticBezier, CubicBezier, Arc
from domain.ports.svg_loader_port import SvgLoaderPort

class SvgLoaderAdapter(SvgLoaderPort):
    " Clase para cargar y extraer paths y atributos de un archivo SVG. "
    def get_paths(self) -> list:
        """Obtiene las rutas del documento SVG cargado."""
        return self.paths

    def get_attributes(self) -> dict:
        """Obtiene los atributos del documento SVG cargado."""
        return self.attributes

    def __init__(self, svg_file: Path):
        super().__init__()
        self.svg_file = svg_file
        self.paths: List[SvgPath] = []
        self.attributes: dict[str, Any] = {}
        self._load()

    def _load(self):
        paths, _, attr = svg2paths2(str(self.svg_file))
        # Normalizar: invertir eje Y de todos los puntos
        if paths:
            # Calcular el máximo Y para invertir respecto a la base del SVG
            all_y = [pt.imag for path in paths for seg in path for pt in [seg.start, seg.end]]
            if all_y:
                ymax = max(all_y)
                def invert_y(pt):
                    return complex(pt.real, ymax - pt.imag)
                def invert_path(path):
                    new_segments = []
                    for seg in path:
                        if isinstance(seg, Line):
                            new_segments.append(Line(invert_y(seg.start), invert_y(seg.end)))
                        elif isinstance(seg, QuadraticBezier):
                            new_segments.append(QuadraticBezier(
                                invert_y(seg.start),
                                invert_y(seg.control),
                                invert_y(seg.end)
                            ))
                        elif isinstance(seg, CubicBezier):
                            new_segments.append(CubicBezier(
                                invert_y(seg.start),
                                invert_y(seg.control1),
                                invert_y(seg.control2),
                                invert_y(seg.end)
                            ))
                        elif isinstance(seg, Arc):
                            new_segments.append(Arc(
                                invert_y(seg.start),
                                seg.radius,
                                seg.rotation,
                                seg.arc,
                                seg.sweep,
                                invert_y(seg.end)
                            ))
                        else:
                            new_segments.append(type(seg)(invert_y(seg.start), invert_y(seg.end)))
                    return SvgPath(*new_segments)
                self.paths = [invert_path(p) for p in paths]
            else:
                self.paths = paths
        else:
            self.paths = paths
        self.attributes = attr
        # Una discontinuidad se detecta si la distancia entre el final de un segmento 
        # y el inicio del siguiente
        # es mayor a una tolerancia.
        # Implementación pendiente o migrada según necesidades del dominio
        return self.paths

    def load(self, file_path: str) -> None:
        """Implementación requerida por SvgLoaderPort. Carga el archivo SVG indicado."""
        self.svg_file = Path(file_path)
        self._load()

"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).
"""

from pathlib import Path
from svgpathtools import Path as SvgPath

from config.config import (
    SVG_INPUT_DIR, GCODE_OUTPUT_DIR,
    FEED, CMD_DOWN, CMD_UP,
    STEP_MM, DWELL_MS, MAX_HEIGHT_MM
)
from infrastructure.svg_loader import SvgLoader
from infrastructure.logger import logger
from domain.gcode_generator import GCodeGenerator
from domain.path_transform_strategy import MirrorVerticalStrategy
from domain.path_filter import PathFilter
from cli.svg_file_selector import SvgFileSelector
from cli.gcode_filename_generator import GcodeFilenameGenerator
from cli.bounding_box_calculator import BoundingBoxCalculator

class SvgToGcodeApp:
    " Main application class for converting SVG files to G-code. "
    def __init__(self):
        self.selector = SvgFileSelector(SVG_INPUT_DIR)
        self.filename_gen = GcodeFilenameGenerator(GCODE_OUTPUT_DIR)
        self.logger = logger
        self.feed = FEED
        self.cmd_down = CMD_DOWN
        self.cmd_up = CMD_UP
        self.step_mm = STEP_MM
        self.dwell_ms = DWELL_MS
        self.max_height_mm = MAX_HEIGHT_MM

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))

    def run(self):
        " Main method to run the SVG to G-code conversion process. "
        # --- Lógica de presentación ---
        svg_file = self.selector.select()
        self.logger.debug("Selected SVG file: %s", svg_file)

        gcode_file = self.filename_gen.next_filename(svg_file)
        self.logger.debug("Output G-code file: %s", gcode_file)

        # --- Lógica de negocio ---
        svg = SvgLoader(svg_file)
        self.logger.debug('Created object "svg" from class "SvgLoader"')
        self.logger.info("Carga de SVG: %s", svg_file)

        paths = svg.get_paths()
        self.logger.debug("Extracted %d paths from SVG.", len(paths))
        self.logger.info("Paths extraídos: %d", len(paths))

        # --- Logging detallado de paths para diagnóstico de continuidad ---
        for i, p in enumerate(paths):
            # Verificar continuidad del path
            is_continuous = getattr(p, 'iscontinuous', lambda: None)()
            self.logger.info(
                "Path %d: iscontinuous=%s, segmentos=%d", i+1, is_continuous, len(p)
            )
            # Registrar tipo de cada segmento
            for j, seg in enumerate(p):
                self.logger.info(
                    "  Segmento %d: tipo=%s, longitud=%.5f",
                    j+1,
                    type(seg).__name__,
                    getattr(seg, 'length', lambda: float('nan'))()
                )
            # Identificar discontinuidades (si aplica)
            discontinuities = []
            for j in range(len(p)-1):
                z_end = p[j].point(1)
                z_next = p[j+1].point(0)
                if abs(z_end - z_next) > 1e-6:
                    discontinuities.append((j, j+1, z_end, z_next))
            if discontinuities:
                self.logger.warning(
                    "  Discontinuidades detectadas en path %d: %s",
                    i+1,
                    [f"seg{a}->seg{b} ({z1:.3f}->{z2:.3f})"
                     for a,b,z1,z2 in discontinuities]
                )
            else:
                self.logger.info("  Path %d: sin discontinuidades detectadas", i+1)
        # --- Fin logging detallado ---

        # Instrumentación: imprimir puntos de inicio y fin de cada path SVG real
        for i, p in enumerate(paths):
            xs, ys = [], []
            for seg in p:
                z0 = seg.point(0)
                z1 = seg.point(1)
                xs.extend([z0.real, z1.real])
                ys.extend([z0.imag, z1.imag])
            if xs and ys:
                self.logger.info(
                    "Path %d: inicio=(%.3f, %.3f), fin=(%.3f, %.3f)",
                    i+1, xs[0], ys[0], xs[-1], ys[-1]
                )

        # --- Dividir paths discontinuos en subpaths continuos ---
        all_subpaths = []
        for i, p in enumerate(paths):
            subpaths = split_path_into_continuous_subpaths(p)
            if len(subpaths) > 1:
                self.logger.warning(
                "Path %d dividido en %d subpaths continuos "
                "por discontinuidades.", i+1, len(subpaths))
            all_subpaths.extend(subpaths)
        paths = all_subpaths
        self.logger.info("Total de subpaths continuos tras división: %d", len(paths))
        # --- Fin división de paths ---

        # Filtrar paths triviales
        path_filter = PathFilter(min_length=1e-3)
        paths = path_filter.filter_nontrivial(paths)
        self.logger.info("Paths útiles tras filtrado: %d", len(paths))

        svg_attr = svg.get_attributes()
        self.logger.debug("SVG attributes: %s", svg_attr)
        self.logger.info("SVG attributes: %s", svg_attr)

        # --- Logging detallado de atributos SVG para diagnóstico ---
        self.logger.info("SVG atributos (tipos):")
        for k, v in svg_attr.items():
            self.logger.info("  %s: tipo=%s, valor=%r", k, type(v).__name__, v)
        # Identificar atributos relevantes
        relevantes = ["stroke-dasharray", "fill-rule", "stroke", "fill", "style"]
        for r in relevantes:
            if r in svg_attr:
                self.logger.info("  [RELEVANTE] %s: %r", r, svg_attr[r])
        # --- Fin logging atributos SVG ---

        # Calcular bbox y centro para las estrategias
        try:
            bbox = (svg.get_bbox()
                    if hasattr(svg, 'get_bbox')
                    else BoundingBoxCalculator.calculate_bbox(paths))
        except (AttributeError, ValueError):
            bbox = BoundingBoxCalculator.calculate_bbox(paths)
        _xmin, _xmax, _ymin, _ymax = bbox
        _cx, cy = BoundingBoxCalculator.center(bbox)
        self.logger.info(
            "Bounding box: xmin=%.3f, xmax=%.3f, "
            "ymin=%.3f, ymax=%.3f",
            _xmin, _xmax, _ymin, _ymax)
        # Definir estrategias de transformación (ejemplo: vertical mirror)
        transform_strategies = [MirrorVerticalStrategy(cy)]
        self.logger.info("Estrategias de transformación: %s", transform_strategies)

        generator = GCodeGenerator(
            feed=self.feed,
            cmd_down=self.cmd_down,
            cmd_up=self.cmd_up,
            step_mm=self.step_mm,
            dwell_ms=self.dwell_ms,
            max_height_mm=self.max_height_mm,
            logger=self.logger,
            transform_strategies=transform_strategies
        )

        self.logger.debug("Initialized GCodeGenerator with parameters: %s", generator)

        # --- Lógica de IO separada de la lógica de negocio ---
        gcode_lines = generator.generate(paths, svg_attr)
        self.logger.debug("Generated G-code with %d lines.", len(gcode_lines))
        self.logger.info("G-code generado con %d líneas", len(gcode_lines))

        self._write_gcode_file(gcode_file, gcode_lines)
        self.logger.info("Archivo G-code escrito: %s", gcode_file)

def split_path_into_continuous_subpaths(path, tol=1e-6):
    """
    Divide un path en subpaths continuos.
    Args:
        path: Un objeto Path de svgpathtools (o similar, iterable de segmentos).
        tol: Tolerancia para considerar dos puntos como conectados.
    Returns:
        Lista de subpaths (cada uno es un objeto Path de svgpathtools).
    """
    if not path:
        return []
    subpaths = []
    current = [path[0]]
    for seg_prev, seg_next in zip(path, path[1:]):
        if abs(seg_prev.point(1) - seg_next.point(0)) < tol:
            current.append(seg_next)
        else:
            subpaths.append(SvgPath(*current))
            current = [seg_next]
    if current:
        subpaths.append(SvgPath(*current))
    return subpaths

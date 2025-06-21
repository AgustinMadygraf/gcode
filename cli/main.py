"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).
"""

from pathlib import Path
import sys

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

    def _select_svg_file(self) -> Path:
        svg_dir = SVG_INPUT_DIR
        svg_files = sorted(svg_dir.glob("*.svg"))
        if not svg_files:
            sys.exit("No SVG files found in svg_input.")
        self.logger.info("Available SVG files:")
        for idx, f in enumerate(svg_files, 1):
            self.logger.info("  %d. %s", idx, f.name)
        while True:
            try:
                sel = int(input(f"Select an SVG file (1-{len(svg_files)}): "))
                if 1 <= sel <= len(svg_files):
                    return svg_files[sel-1]
            except (ValueError, TypeError):
                pass
            self.logger.warning("Invalid selection. Try again.")

    def _next_gcode_filename(self, svg_file: Path) -> Path:
        out_dir = GCODE_OUTPUT_DIR
        stem = svg_file.stem
        for i in range(100):
            candidate = out_dir / f"{stem}_v{i:02d}.gcode"
            if not candidate.exists():
                return candidate
        sys.exit("Too many output files for this SVG.")

    def _filter_nontrivial_paths(self, paths, min_length=1e-3):
        filtered = []
        for i, p in enumerate(paths):
            total_length = sum(seg.length() for seg in p)
            if total_length > min_length:
                filtered.append(p)
            else:
                self.logger.info(
                    "Path %d omitido por longitud despreciable: %.6f",
                    i+1, total_length)
        return filtered

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

        # Filtrar paths triviales
        path_filter = PathFilter(min_length=1e-3)
        paths = path_filter.filter_nontrivial(paths)
        self.logger.info("Paths útiles tras filtrado: %d", len(paths))

        svg_attr = svg.get_attributes()
        self.logger.debug("SVG attributes: %s", svg_attr)
        self.logger.info("SVG attributes: %s", svg_attr)

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

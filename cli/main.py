"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).
"""

from pathlib import Path

from config.config import (
    SVG_INPUT_DIR, GCODE_OUTPUT_DIR,
    FEED, CMD_DOWN, CMD_UP,
    STEP_MM, DWELL_MS, MAX_HEIGHT_MM,
    REMOVE_SVG_BORDER, BORDER_DETECTION_TOLERANCE
)
from domain.path_transform_strategy import MirrorVerticalStrategy
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.gcode_compression.gcode_compression_service import GcodeCompressionService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from infrastructure.compressors.arc_compressor import ArcCompressor
from infrastructure.adapters.config_adapter import ConfigAdapter
from cli.svg_file_selector import SvgFileSelector
from cli.gcode_filename_generator import GcodeFilenameGenerator
from cli.bounding_box_calculator import BoundingBoxCalculator
from infrastructure.logger import logger
from infrastructure.svg_loader import SvgLoader
from infrastructure.adapters.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from infrastructure.path_sampler import PathSampler

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
        svg_file = self.selector.select()
        self.logger.debug("Selected SVG file: %s", svg_file)
        gcode_file = self.filename_gen.next_filename(svg_file)
        self.logger.debug("Output G-code file: %s", gcode_file)

        svg = SvgLoader(svg_file)
        self.logger.debug('Created object "svg" from class "SvgLoader"')
        self.logger.info("Carga de SVG: %s", svg_file)

        paths = svg.get_paths()
        self.logger.debug("Extracted %d paths from SVG.", len(paths))
        self.logger.info("Paths extraídos: %d", len(paths))

        svg_attr = svg.get_attributes()
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
        # Definir estrategias de transformación (mirror vertical para invertir eje Y SVG)
        transform_strategies = [MirrorVerticalStrategy(cy)]
        self.logger.info("Estrategias de transformación: %s", transform_strategies)

        # --- Procesamiento de paths mediante servicio de dominio ---
        path_processor = PathProcessingService(
            min_length=1e-3,
            remove_svg_border=REMOVE_SVG_BORDER,
            border_tolerance=BORDER_DETECTION_TOLERANCE
            # No pasar transform_strategies aquí, solo filtra y divide
        )
        processed_paths = path_processor.process(paths, svg_attr)
        self.logger.info("Paths útiles tras procesamiento: %d", len(processed_paths))

        # --- Generación de G-code mediante servicio de dominio ---
        path_sampler = PathSampler(self.step_mm, logger=self.logger)
        generator: GcodeGeneratorPort = GCodeGeneratorAdapter(
            path_sampler=path_sampler,
            feed=self.feed,
            cmd_down=self.cmd_down,
            cmd_up=self.cmd_up,
            step_mm=self.step_mm,
            dwell_ms=self.dwell_ms,
            max_height_mm=self.max_height_mm,
            logger=self.logger,
            transform_strategies=transform_strategies
        )
        gcode_service = GCodeGenerationService(generator)
        gcode_lines = gcode_service.generate(processed_paths, svg_attr)
        self.logger.debug("Generated G-code with %d lines.", len(gcode_lines))
        self.logger.info("G-code generado con %d líneas", len(gcode_lines))

        # --- Compresión de G-code mediante caso de uso ---
        compressors = [ArcCompressor()]
        compression_service = GcodeCompressionService(compressors, logger=self.logger)
        config_reader = ConfigAdapter()
        compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
        compression_result = compress_use_case.execute(gcode_lines)
        compressed_gcode = compression_result['compressed_gcode'] if 'compressed_gcode' in compression_result else gcode_lines
        # Mostrar métricas
        self.logger.info("Compresión: original=%d, comprimido=%d, ratio=%.2f%%", 
            compression_result.get('original_size', 0),
            compression_result.get('compressed_size', 0),
            100 * (1 - compression_result.get('compression_ratio', 1)))

        self._write_gcode_file(gcode_file, compressed_gcode)
        self.logger.info("Archivo G-code escrito: %s", gcode_file)

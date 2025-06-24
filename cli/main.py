"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).
"""

from pathlib import Path
from infrastructure.config.config import Config
from adapters.input.config_adapter import ConfigAdapter
from domain.ports.config_port import ConfigPort
from domain.ports.config_provider import ConfigProviderPort
from domain.path_transform_strategy import MirrorVerticalStrategy
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.gcode_compression.gcode_compression_service import GcodeCompressionService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from infrastructure.compressors.arc_compressor import ArcCompressor
from cli.svg_file_selector import SvgFileSelector
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from adapters.input.path_sampler import PathSampler
from domain.services.geometry import GeometryService
from application.use_cases.file_output.filename_service import FilenameService
from infrastructure.factories.container import Container
from domain.ports.logger_port import LoggerPort

class SvgToGcodeApp:
    " Main application class for converting SVG files to G-code. "
    def __init__(self):
        self.container = Container()
        self.config = self.container.config
        self.config_port = self.container.config_port
        self.selector = self.container.selector
        self.filename_gen = self.container.filename_gen
        self.logger: LoggerPort = self.container.logger
        self.feed = self.container.feed
        self.cmd_down = self.container.cmd_down
        self.cmd_up = self.container.cmd_up
        self.step_mm = self.container.step_mm
        self.dwell_ms = self.container.dwell_ms
        self.max_height_mm = self.container.max_height_mm
        self.max_width_mm = self.container.max_width_mm

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))

    def run(self):
        " Main method to run the SVG to G-code conversion process. "
        try:
            svg_file = self.selector.select()
        except FileNotFoundError:
            self.logger.error("La carpeta configurada para SVG está vacía o no contiene archivos SVG.")
            return
        self.logger.debug("Selected SVG file: %s", svg_file)
        gcode_file = self.filename_gen.next_filename(svg_file)
        self.logger.debug("Output G-code file: %s", gcode_file)

        svg_loader = self.container.get_svg_loader(svg_file)
        self.logger.debug('Created object "svg_loader" from SvgLoaderPort')
        self.logger.info("Carga de SVG: %s", svg_file)

        paths = svg_loader.get_paths()
        self.logger.debug("Extracted %d paths from SVG.", len(paths))
        self.logger.info("Paths extraídos: %d", len(paths))

        svg_attr = svg_loader.get_attributes()
        self.logger.info("SVG attributes: %s", svg_attr)

        # Calcular bbox y centro usando GeometryService
        try:
            bbox = GeometryService._calculate_bbox(paths)
        except (AttributeError, ValueError):
            bbox = (0, 0, 0, 0)
        _xmin, _xmax, _ymin, _ymax = bbox
        _cx, cy = GeometryService._center(bbox)
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
            remove_svg_border=self.config.get_remove_svg_border(),
            border_tolerance=self.config.get_border_detection_tolerance()
        )
        processed_paths = path_processor.process(paths, svg_attr)
        self.logger.info("Paths útiles tras procesamiento: %d", len(processed_paths))

        # --- Generación de G-code mediante servicio de dominio ---
        generator: GcodeGeneratorPort = self.container.get_gcode_generator(transform_strategies=transform_strategies)
        gcode_service = GCodeGenerationService(generator)
        gcode_lines = gcode_service.generate(processed_paths, svg_attr)
        self.logger.debug("Generated G-code with %d lines.", len(gcode_lines))
        self.logger.info("G-code generado con %d líneas", len(gcode_lines))

        # --- Compresión de G-code mediante caso de uso ---
        compressors = [ArcCompressor()]
        compression_service = GcodeCompressionService(compressors, logger=self.logger)
        config_reader = ConfigAdapter(self.config)
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

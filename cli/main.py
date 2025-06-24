"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).

Nota: Este módulo NO debe ejecutarse directamente. El único punto de entrada soportado es run.py
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
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from adapters.input.path_sampler import PathSampler
from domain.services.geometry import GeometryService
from domain.services.filename_service import FilenameService
from infrastructure.factories.container import Container
from domain.ports.logger_port import LoggerPort
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.infra_factory import InfraFactory
from application.exceptions import AppError, DomainError, InfrastructureError
from domain.ports.file_selector_port import FileSelectorPort
from cli.svg_file_selector_adapter import SvgFileSelectorAdapter

class SvgToGcodeApp:
    " Main application class for converting SVG files to G-code. "
    def __init__(self):
        file_selector: FileSelectorPort = SvgFileSelectorAdapter()
        self.container = Container(file_selector=file_selector)
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
        self.event_bus = self.container.event_bus
        # Suscribimos un handler de ejemplo al evento 'gcode_generated'
        self.event_bus.subscribe('gcode_generated', self._on_gcode_generated)

    def _on_gcode_generated(self, payload):
        self.logger.info(f"[EVENTO] G-code generado para: {payload['svg_file']} → {payload['gcode_file']}")

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))

    def run(self):
        " Main method to run the SVG to G-code conversion process. "
        try:
            svg_file = self.selector.select_svg_file()
            if not svg_file:
                self.logger.error("No se seleccionó un archivo SVG válido. Operación cancelada.")
                print("[ERROR] No se seleccionó un archivo SVG válido. El proceso ha sido cancelado.")
                return
            svg_file = Path(svg_file)  # Asegura que sea un Path
            self.logger.debug("Selected SVG file: %s", svg_file)
            gcode_file = self.filename_gen.next_filename(svg_file)
            self.logger.debug("Output G-code file: %s", gcode_file)

            # Calcular bbox y centro usando GeometryService
            svg_loader_factory = self.container.get_svg_loader
            paths = svg_loader_factory(svg_file).get_paths()
            try:
                bbox = DomainFactory.create_geometry_service()._calculate_bbox(paths)
            except (AttributeError, ValueError):
                bbox = (0, 0, 0, 0)
            _xmin, _xmax, _ymin, _ymax = bbox
            _cx, cy = DomainFactory.create_geometry_service()._center(bbox)
            transform_strategies = [MirrorVerticalStrategy(cy)]

            # Instanciar servicios/casos de uso usando factories
            path_processor = PathProcessingService(
                min_length=1e-3,
                remove_svg_border=self.config.get_remove_svg_border(),
                border_tolerance=self.config.get_border_detection_tolerance()
            )
            generator = self.container.get_gcode_generator(transform_strategies=transform_strategies)
            gcode_service = GCodeGenerationService(generator)
            compressors = [ArcCompressor()]
            compression_service = GcodeCompressionService(compressors, logger=self.logger)
            config_reader = AdapterFactory.create_config_adapter(self.config)
            compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
            svg_to_gcode_use_case = SvgToGcodeUseCase(
                svg_loader_factory=svg_loader_factory,
                path_processing_service=path_processor,
                gcode_generation_service=gcode_service,
                gcode_compression_use_case=compress_use_case,
                logger=self.logger,
                filename_service=self.filename_gen
            )
            # Ejecutar caso de uso
            result = svg_to_gcode_use_case.execute(svg_file, transform_strategies=transform_strategies)
            self._write_gcode_file(gcode_file, result['compressed_gcode'])
            self.logger.info("Archivo G-code escrito: %s", gcode_file)
            # Publicar evento tras generar el archivo
            self.event_bus.publish('gcode_generated', {'svg_file': svg_file, 'gcode_file': gcode_file})
        except FileNotFoundError:
            self.logger.error("La carpeta configurada para SVG está vacía o no contiene archivos SVG.")
        except DomainError as de:
            self.logger.error(f"Error de dominio: {de}")
            print(f"[ERROR DOMINIO] {de}")
        except InfrastructureError as ie:
            self.logger.error(f"Error de infraestructura: {ie}")
            print(f"[ERROR INFRAESTRUCTURA] {ie}")
        except AppError as ae:
            self.logger.error(f"Error de aplicación: {ae}")
            print(f"[ERROR APLICACIÓN] {ae}")
        except Exception as ex:
            self.logger.error(f"Error inesperado: {ex}", exc_info=True)
            print(f"[ERROR INESPERADO] {ex}")

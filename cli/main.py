"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).

Nota: Este módulo NO debe ejecutarse directamente. El único punto de entrada soportado es run.py
"""

from pathlib import Path
import time
from infrastructure.config.config import Config
from adapters.input.config_adapter import ConfigAdapter
from domain.ports.config_port import ConfigPort
from domain.ports.config_provider import ConfigProviderPort
from domain.services.path_transform_strategies import MirrorVerticalStrategy
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.gcode_compression.gcode_compression_service import GcodeCompressionService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from infrastructure.compressors.arc_compressor import ArcCompressor
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from adapters.input.path_sampler import PathSampler
from domain.services.geometry import GeometryService
from infrastructure.factories.container import Container
from domain.ports.logger_port import LoggerPort
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.infra_factory import InfraFactory
from application.exceptions import AppError, DomainError, InfrastructureError
from infrastructure.error_handling import ExceptionHandler
from domain.ports.file_selector_port import FileSelectorPort
from adapters.input.svg_file_selector_adapter import SvgFileSelectorAdapter
from adapters.input.gcode_file_selector_adapter import GcodeFileSelectorAdapter
from application.use_cases.gcode_to_gcode_use_case import GcodeToGcodeUseCase
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
from domain.ports.filename_service_port import FilenameServicePort
from cli.i18n import I18n
from cli.terminal_colors import TerminalColors
from cli.user_config import UserConfig
from cli.progress_bar import print_progress_bar
from cli.presenters.cli_presenter import CliPresenter
from cli.operations.svg_to_gcode import SvgToGcodeOperation
from cli.operations.gcode_to_gcode import GcodeToGcodeOperation
from application.workflows.svg_to_gcode_workflow import SvgToGcodeWorkflow
from application.workflows.gcode_to_gcode_workflow import GcodeToGcodeWorkflow

class SvgToGcodeApp:
    """ Main application class for converting SVG files to G-code. """
    def __init__(self, args=None):
        file_selector: FileSelectorPort = SvgFileSelectorAdapter()
        self.container = Container(file_selector=file_selector)
        self.filename_service: FilenameServicePort = self.container.filename_gen
        self.config = self.container.config
        self.config_port = self.container.config_port
        self.selector = self.container.selector
        self.logger: LoggerPort = self.container.logger
        self.feed = self.container.feed
        self.cmd_down = self.container.cmd_down
        self.cmd_up = self.container.cmd_up
        self.step_mm = self.container.step_mm
        self.dwell_ms = self.container.dwell_ms
        self.max_height_mm = self.container.max_height_mm
        self.max_width_mm = self.container.max_width_mm
        self.event_bus = self.container.event_bus
        self.args = args
        self.interactive_mode = True if args is None else not getattr(args, 'no_interactive', False)
        self.use_colors = False if args is None else not getattr(args, 'no_color', False)
        self.language = getattr(args, 'lang', 'es') if args else 'es'
        self.i18n = I18n(self.language)
        self.colors = TerminalColors(self.use_colors)
        self.presenter = CliPresenter(i18n=self.i18n, color_service=self.colors)
        self.user_config = UserConfig()
        # Cargar preferencias desde archivo personalizado si se indica
        if args and getattr(args, 'config', None):
            import json
            try:
                with open(args.config, 'r', encoding='utf-8') as f:
                    self.user_config.data.update(json.load(f))
            except Exception:
                pass
        # Sobrescribir args con preferencias guardadas si existen
        if args:
            for key in ["lang", "no_color", "input", "output"]:
                if getattr(args, key, None) is None and self.user_config.get(key) is not None:
                    setattr(args, key, self.user_config.get(key))
        # Guardar preferencias si se solicita
        if args and getattr(args, 'save_config', False):
            self.user_config.update_from_args(args)
        # Suscribimos un handler de ejemplo al evento 'gcode_generated'
        self.event_bus.subscribe('gcode_generated', self._on_gcode_generated)
        # Suscribimos handler para evento de reescalado
        self.event_bus.subscribe('gcode_rescaled', self._on_gcode_rescaled)
        self.svg_to_gcode_workflow = SvgToGcodeWorkflow(self.container, self.presenter, self.filename_service, self.config)
        self.gcode_to_gcode_workflow = GcodeToGcodeWorkflow(self.container, self.presenter, self.filename_service, self.config)
        self.operations = {
            1: SvgToGcodeOperation(self.svg_to_gcode_workflow, self.selector),
            2: GcodeToGcodeOperation(self.gcode_to_gcode_workflow, self.config)
        }

    def _on_gcode_generated(self, payload):
        self.presenter.print_event('gcode_generated', payload)

    def _on_gcode_rescaled(self, payload):
        self.presenter.print_event('gcode_rescaled', payload)

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))
            
    def _get_context_info(self):
        """Obtener información de contexto para el manejo de excepciones"""
        return {
            "app_version": "1.3.0",
            "config_loaded": bool(self.config),
            "max_dimensions": f"{self.max_width_mm}x{self.max_height_mm}mm"
        }
    
    def _print(self, key, color=None, **kwargs):
        msg = self.i18n.get(key, **kwargs)
        self.presenter.print(msg, color=color)

    def select_operation_mode(self):
        self._print("menu_title", color='bold')
        self._print("option_svg_to_gcode")
        self._print("option_optimize")
        while True:
            try:
                choice = int(self.presenter.input(self.i18n.get("enter_number") + ": "))
                if choice in [1, 2]:
                    return choice
                self._print("invalid_selection", color='yellow')
            except ValueError:
                self._print("invalid_number", color='yellow')

    def _process_with_progress(self, items, process_func, prefix='Procesando'):
        total = len(items)
        for i, item in enumerate(items, 1):
            process_func(item)
            self.presenter.print_progress(i, total, prefix=prefix)

    def run(self):
        """Método principal que ejecuta la aplicación"""
        error_handler = self.container.error_handler
        if self.interactive_mode:
            operation_mode = self.select_operation_mode()
            operation = self.operations.get(operation_mode)
            if operation:
                result = error_handler.wrap_execution(
                    operation.execute,
                    self._get_context_info()
                )
            else:
                self.presenter.print(self.i18n.get("invalid_selection"), color='yellow')
                return 1
            if not result.get('success', False):
                error_info = result.get('message', 'Error desconocido')
                error_type = result.get('error', 'Error')
                self.presenter.print(f"[{error_type.upper()}] {error_info}", color='red')
                return 1
            return 0
        else:
            return self._run_non_interactive()

    def _run_non_interactive(self):
        """Ejecuta el flujo no interactivo basado en argumentos CLI"""
        if not self.args or not self.args.input:
            self._print("error_file_not_found", color='red')
            return 2
        input_path = self.args.input
        output_path = self.args.output
        optimize = getattr(self.args, 'optimize', False)
        rescale = getattr(self.args, 'rescale', None)
        # SVG a GCODE
        if str(input_path).lower().endswith('.svg'):
            svg_loader_factory = self.container.get_svg_loader
            self._print("processing_start", color='blue')
            paths = svg_loader_factory(input_path).get_paths()
            self._print("processing_complete", color='green')
            bbox = DomainFactory.create_geometry_service()._calculate_bbox(paths)
            _xmin, _xmax, _ymin, _ymax = bbox
            _cx, cy = DomainFactory.create_geometry_service()._center(bbox)
            transform_strategies = []
            if self.config.get_mirror_vertical():
                transform_strategies.append(MirrorVerticalStrategy(cy))
            path_processor = PathProcessingService(
                min_length=1e-3,
                remove_svg_border=self.config.get_remove_svg_border(),
                border_tolerance=self.config.get_border_detection_tolerance()
            )
            generator = self.container.get_gcode_generator(transform_strategies=transform_strategies)
            gcode_service = GCodeGenerationService(generator)
            compression_service = create_gcode_compression_service(logger=self.logger)
            config_reader = AdapterFactory.create_config_adapter(self.config)
            compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
            svg_to_gcode_use_case = SvgToGcodeUseCase(
                svg_loader_factory=svg_loader_factory,
                path_processing_service=path_processor,
                gcode_generation_service=gcode_service,
                gcode_compression_use_case=compress_use_case,
                logger=self.logger,
                filename_service=self.filename_service
            )
            result = svg_to_gcode_use_case.execute(input_path, transform_strategies=transform_strategies)
            gcode_lines = result['compressed_gcode'] if optimize else result['gcode']
            out_file = output_path or self.filename_service.next_filename(input_path)
            self._write_gcode_file(out_file, gcode_lines)
            self._print("processing_complete", color='green')
            self._print("success_refactor", color='green', output_file=out_file)
            return 0
        # GCODE a GCODE
        elif str(input_path).lower().endswith('.gcode'):
            if optimize:
                refactor_use_case = GcodeToGcodeUseCase(
                    filename_service=self.filename_service,
                    logger=self.logger
                )
                result = refactor_use_case.execute(input_path)
                out_file = output_path or result['output_file']
                self._print("success_refactor", color='green', output_file=out_file)
                self._print("success_optimize", color='green', changes=result['changes_made'])
                return 0
            elif rescale:
                from application.use_cases.gcode_rescale_use_case import GcodeRescaleUseCase
                rescale_use_case = GcodeRescaleUseCase(
                    filename_service=self.filename_service,
                    logger=self.logger,
                    config_provider=self.config
                )
                result = rescale_use_case.execute(input_path, rescale)
                out_file = output_path or result['output_file']
                original_dim = result['original_dimensions']
                new_dim = result['new_dimensions']
                self._print("success_rescale", color='green', output_file=out_file)
                self._print("rescale_original", width=original_dim['width'], height=original_dim['height'])
                self._print("rescale_new", width=new_dim['width'], height=new_dim['height'])
                self._print("rescale_factor", factor=result['scale_factor'])
                self._print("rescale_cmds", g0g1=result['commands_rescaled']['g0g1'], g2g3=result['commands_rescaled']['g2g3'])
                return 0
            else:
                self._print("error_occurred", color='red')
                return 3
        else:
            self._print("error_occurred", color='red')
            return 3

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
from cli.user_config_manager import ConfigManager
from cli.progress_bar import print_progress_bar
from cli.presenters.cli_presenter import CliPresenter
from cli.operations.svg_to_gcode import SvgToGcodeOperation
from cli.operations.gcode_to_gcode import GcodeToGcodeOperation
from application.workflows.svg_to_gcode_workflow import SvgToGcodeWorkflow
from application.workflows.gcode_to_gcode_workflow import GcodeToGcodeWorkflow
from application.workflows.non_interactive_svg_to_gcode_workflow import NonInteractiveSvgToGcodeWorkflow
from cli.modes.interactive import InteractiveModeStrategy
from cli.modes.non_interactive import NonInteractiveModeStrategy
from domain.events.event_bus import EventBus
from domain.events.events import GcodeGeneratedEvent, GcodeRescaledEvent

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
        self.event_bus = EventBus()
        self.args = args
        self.interactive_mode = True if args is None else not getattr(args, 'no_interactive', False)
        self.use_colors = False if args is None else not getattr(args, 'no_color', False)
        self.language = getattr(args, 'lang', 'es') if args else 'es'
        self.i18n = I18n(self.language)
        self.colors = TerminalColors(self.use_colors)
        self.presenter = CliPresenter(i18n=self.i18n, color_service=self.colors)
        self.config_manager = ConfigManager(args)
        self.user_config = self.config_manager.user_config
        # Suscribimos un handler de ejemplo al evento 'gcode_generated'
        self.event_bus.subscribe(GcodeGeneratedEvent, self._on_gcode_generated)
        # Suscribimos handler para evento de reescalado
        self.event_bus.subscribe(GcodeRescaledEvent, self._on_gcode_rescaled)
        self.svg_to_gcode_workflow = SvgToGcodeWorkflow(self.container, self.presenter, self.filename_service, self.config)
        self.gcode_to_gcode_workflow = GcodeToGcodeWorkflow(self.container, self.presenter, self.filename_service, self.config)
        self.non_interactive_workflow = NonInteractiveSvgToGcodeWorkflow(
            self.container, self.presenter, self.filename_service, self.config
        )
        self.operations = {
            1: SvgToGcodeOperation(self.svg_to_gcode_workflow, self.selector),
            2: GcodeToGcodeOperation(self.gcode_to_gcode_workflow, self.config)
        }
        self.mode_strategy = InteractiveModeStrategy() if self.interactive_mode else NonInteractiveModeStrategy()

    def _on_gcode_generated(self, event: GcodeGeneratedEvent):
        self.presenter.print_event('gcode_generated', {
            'output_file': event.output_file,
            'lines': event.lines,
            'metadata': event.metadata
        })

    def _on_gcode_rescaled(self, event: GcodeRescaledEvent):
        self.presenter.print_event('gcode_rescaled', {
            'output_file': event.output_file,
            'original_dimensions': event.original_dimensions,
            'new_dimensions': event.new_dimensions,
            'scale_factor': event.scale_factor,
            'commands_rescaled': event.commands_rescaled
        })

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
        return self.mode_strategy.run(self)

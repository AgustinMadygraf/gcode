"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).

Nota: Este módulo NO debe ejecutarse directamente. El único punto de entrada soportado es run.py
"""

from pathlib import Path
import time
import locale
import os
import sys
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
from infrastructure.i18n.i18n_service import I18nService
from cli.i18n import MESSAGES
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
from application.orchestrator import ApplicationOrchestrator
from infrastructure.events.event_manager import EventManager
from cli.utils.i18n_utils import detect_language
from cli.utils.terminal_utils import supports_color
from cli.utils.cli_event_manager import CliEventManager

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
        self.args = args
        self.interactive_mode = True if args is None else not getattr(args, 'no_interactive', False)
        # Detección automática de soporte de colores (refactorizado)
        self.use_colors = supports_color(args)
        # Detección automática de idioma (refactorizado)
        self.language = detect_language(args)
        self.i18n = I18nService(MESSAGES, default_lang=self.language)
        self.colors = TerminalColors(self.use_colors)
        self.presenter = CliPresenter(i18n=self.i18n, color_service=self.colors)
        self.config_manager = ConfigManager(args)
        self.user_config = self.config_manager.user_config
        # --- Nueva gestión de eventos (refactor: delegada) ---
        self.event_manager = CliEventManager(self.presenter)
        # --- Workflows y operaciones ---
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
        # --- Orquestador ---
        self.orchestrator = ApplicationOrchestrator(
            container=self.container,
            presenter=self.presenter,
            filename_service=self.filename_service,
            config=self.config,
            event_bus=self.event_manager,
            workflows={
                'svg_to_gcode': self.svg_to_gcode_workflow,
                'gcode_to_gcode': self.gcode_to_gcode_workflow,
                'non_interactive': self.non_interactive_workflow
            },
            operations=self.operations,
            mode_strategy=self.mode_strategy,
            args=args
        )

    def run(self):
        """Método principal que ejecuta la aplicación"""
        # Antes: return self.orchestrator.run()
        # Ahora: delega en la estrategia de modo, pasando self
        return self.mode_strategy.run(self)

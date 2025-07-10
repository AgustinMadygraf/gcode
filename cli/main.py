"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).

Nota: Este módulo NO debe ejecutarse directamente. El único punto de entrada soportado es run.py
"""

from infrastructure.logger import get_logger, get_dev_logger

from domain.ports.filename_service_port import FilenameServicePort
from application.workflows.svg_to_gcode_workflow import SvgToGcodeWorkflow
from application.workflows.gcode_to_gcode_workflow import GcodeToGcodeWorkflow
from application.workflows.non_interactive_svg_to_gcode_workflow import NonInteractiveSvgToGcodeWorkflow
from application.orchestrator import ApplicationOrchestrator
from cli.terminal_colors import TerminalColors
from cli.user_config_manager import ConfigManager
from cli.presenters.cli_presenter import CliPresenter
from cli.operations.svg_to_gcode import SvgToGcodeOperation
from cli.operations.gcode_to_gcode import GcodeToGcodeOperation
from cli.modes.interactive import InteractiveModeStrategy
from cli.modes.non_interactive import NonInteractiveModeStrategy
from cli.utils.terminal_utils import supports_color
from cli.utils.cli_event_manager import CliEventManager

class SvgToGcodeApp:
    """ Main application class for converting SVG files to G-code. """
    def __init__(self, args=None, container=None):
        self.container = container
        self.logger = container.logger
        self.i18n = container.i18n

        self.filename_service: FilenameServicePort = self.container.filename_gen
        self.config = self.container.config
        self.config_port = self.container.config_port
        self.selector = self.container.selector
        self.feed = self.container.feed
        self.cmd_down = self.container.cmd_down
        self.cmd_up = self.container.cmd_up
        self.step_mm = self.container.step_mm
        self.dwell_ms = self.container.dwell_ms
        self.max_height_mm = self.container.config.plotter_max_area_mm[1]
        self.max_width_mm = self.container.max_width_mm
        self.args = args
        self.interactive_mode = True if args is None else not getattr(args, 'no_interactive', False)
        # Detección automática de soporte de colores (refactorizado)
        self.use_colors = supports_color(args)
        # Selección de logger según modo dev
        if args and getattr(args, 'dev', False):
            self.logger = get_dev_logger(use_color=self.use_colors)
        else:
            self.logger = get_logger(use_color=self.use_colors)
        # Detección automática de idioma (refactorizado)
        self.colors = TerminalColors(self.use_colors)
        self.presenter = CliPresenter(i18n=self.i18n, color_service=self.colors, logger_instance=self.logger)
        self.config_manager = ConfigManager(args)
        self.user_config = self.config_manager.user_config
        # --- Nueva gestión de eventos (refactor: delegada) ---
        self.event_manager = CliEventManager(self.presenter)
        # --- Workflows y operaciones ---
        self.svg_to_gcode_workflow = SvgToGcodeWorkflow(self.container, self.presenter, self.filename_service, self.config)
        self.gcode_to_gcode_workflow = GcodeToGcodeWorkflow(
            self.container,
            self.presenter,
            self.filename_service,
            self.config
        )
        self.non_interactive_workflow = NonInteractiveSvgToGcodeWorkflow(
            self.container, self.presenter, self.filename_service, self.config
        )
        self.operations = {
            1: SvgToGcodeOperation(self.svg_to_gcode_workflow, self.selector),
            2: GcodeToGcodeOperation(self.gcode_to_gcode_workflow, self.config)
        }
        self.mode_strategy = (
            InteractiveModeStrategy()
            if self.interactive_mode
            else NonInteractiveModeStrategy()
        )
        # --- Orquestador ---
        self.orchestrator = ApplicationOrchestrator(
            container=self.container,
            services={
                'filename_service': self.filename_service,
                'config': self.config,
                'event_bus': self.event_manager,
                'workflows': {
                    'svg_to_gcode': self.svg_to_gcode_workflow,
                    'gcode_to_gcode': self.gcode_to_gcode_workflow,
                    'non_interactive': self.non_interactive_workflow
                },
                'operations': self.operations
            },
            mode_strategy=self.mode_strategy,
            i18n=self.i18n,
            args=args
        )

    def run(self):
        """Método principal que ejecuta la aplicación"""
        return self.mode_strategy.run(self)

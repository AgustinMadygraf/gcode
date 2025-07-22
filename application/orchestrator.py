"""
application/orchestrator.py
Orquestador principal de la aplicación. Separa la lógica de orquestación de la UI.
"""


import os
from adapters.input.svg_file_selector_adapter import _find_svg_files_recursively
from infrastructure.logger_helper import LoggerHelper


class ApplicationOrchestrator(LoggerHelper):
    " Orquestador principal de la aplicación SVG2GCODE. "

    def __init__(
        self,
        container,
        services,
        mode_strategy,
        i18n,
        args=None
    ):
        LoggerHelper.__init__(self, config=services.get('config'), logger=getattr(container, 'logger', None))
        self.container = container
        self.i18n = i18n
        # 'services' is a dict or object containing filename_service, config, event_bus, workflows, operations
        self.filename_service = services.get('filename_service')
        self.config = services.get('config')
        self.event_bus = services.get('event_bus')
        self.workflows = services.get('workflows')
        self.operations = services.get('operations')
        self.mode_strategy = mode_strategy
        self.args = args
        self.logger = getattr(container, 'logger', None)

    def run(self):
        " Inicia la ejecución de la aplicación. "
        if self.logger:
            self.logger.info(self.i18n.get('INFO_STARTING_MODE'))
        # Delegar la ejecución al modo de operación (interactivo/no-interactivo)
        result = self.mode_strategy.run(self)
        if self.logger:
            self.logger.info(self.i18n.get('INFO_EXECUTION_FINISHED'))
        return result

    # Métodos para exponer operaciones a la UI (pueden expandirse según necesidades)
    def configure_write_area(self):
        " Configura el área de escritura del plotter. "
        _presets = self.config.get("SURFACE_PRESETS", {})
        plotter_max_area = self.config.plotter_max_area_mm
        # Reemplazar prompt_surface_preset: aquí deberías implementar tu propio input si es necesario
        dims, preset_name = (plotter_max_area, 'personalizado')  # Placeholder, ajusta según tu lógica
        if hasattr(self.config, 'set_target_write_area_mm'):
            self.config.set_target_write_area_mm(dims)
        else:
            self.config.TARGET_WRITE_AREA_MM = dims
        if self.logger:
            self.logger.info(self.i18n.get('SUCCESS_AREA_CONFIGURED', dims0=dims[0], dims1=dims[1], preset_name=preset_name))

    def select_operation_mode(self):
        " Selecciona el modo de operación (interactivo/no-interactivo). "
        args = self.args
        exit_keywords = {'salir', 'exit', 'quit'}
        self._debug(self.i18n.get('DEBUG_SELECTING_MODE'))
        if args and getattr(args, 'no_interactive', False):
            if self.logger:
                self.logger.info(self.i18n.get('INFO_NON_INTERACTIVE_MODE'))
            return None
        if args and getattr(args, 'input', None) and getattr(args, 'output', None):
            if self.logger:
                self.logger.info(self.i18n.get('INFO_DIRECT_EXECUTION'))
            input_file = str(args.input).lower()
            if input_file.endswith('.svg'):
                return 1
            elif input_file.endswith('.gcode'):
                return 2
            elif input_file.endswith('.md'):
                return 3
        svg_dir = './data/svg_input'
        gcode_dir = './data/gcode_output'
        svg_files = []
        gcode_files = []
        try:
            svg_files = _find_svg_files_recursively(svg_dir)
        except ImportError:
            if self.logger:
                self.logger.warning(self.i18n.get('WARN_IMPORT_SVG_SELECTOR'))
        except FileNotFoundError:
            if self.logger:
                self.logger.warning(self.i18n.get('WARN_DIR_NOT_EXISTS', svg_dir=svg_dir))
        except OSError as e:
            if self.logger:
                self.logger.warning(self.i18n.get('WARN_FS_ERROR', error=str(e)))
        try:
            gcode_files = [f for f in os.listdir(gcode_dir) if f.lower().endswith('.gcode')]
        except (FileNotFoundError, OSError):
            pass
        if not svg_files and not gcode_files:
            if self.logger:
                self.logger.warning(self.i18n.get('WARN_NO_FILES_FOUND'))
            if self.logger:
                self.logger.info(self.i18n.get('INFO_OPTIONS'))
            self.logger.option(self.i18n.get('MENU_OPTION_CHANGE_INPUT_DIR'))
            self.logger.option(self.i18n.get('MENU_OPTION_EXIT'))
            while True:
                user_input = self.input_with_label(self.i18n.get('PROMPT_SELECT_OPTION'))
                if user_input.strip() in {'0', 'salir', 'exit', 'quit'}:
                    if self.logger:
                        self.logger.info(self.i18n.get('INFO_EXIT'))
                        self.logger.info(self.i18n.get('INFO_USER_EXIT_REDUCED'))
                    exit(0)
                elif user_input.strip() == '1':
                    if self.logger:
                        self.logger.warning(self.i18n.get('WARN_NOT_IMPLEMENTED'))
                else:
                    if self.logger:
                        self.logger.warning(self.i18n.get('WARN_INVALID_OPTION'))
        while True:
            if self.logger:
                self.logger.info(self.i18n.get('MENU_MAIN_TITLE'))
            self.logger.option(self.i18n.get('MENU_OPTION_CONVERT'))
            self.logger.option(self.i18n.get('MENU_OPTION_OPTIMIZE'))
            self.logger.option(self.i18n.get('MENU_OPTION_MARKDOWN'))
            self.logger.option(self.i18n.get('MENU_OPTION_CONFIGURE_AREA'))
            try:
                user_input = self.input_with_label(self.i18n.get('PROMPT_SELECT_OPTION'))
                if user_input.strip().lower() in exit_keywords:
                    if self.logger:
                        self.logger.info(self.i18n.get('INFO_EXIT'))
                        self.logger.info(self.i18n.get('INFO_USER_EXIT_MAIN'))
                    exit(0)
                choice = int(user_input)
                if choice in [1, 2, 3]:
                    self._debug(self.i18n.get('DEBUG_USER_SELECTED_OP', choice=choice))
                    return choice
                elif choice == 4:
                    self.configure_write_area()
                else:
                    if self.logger:
                        self.logger.warning(self.i18n.get('WARN_INVALID_SELECTION'))
            except ValueError:
                if self.logger:
                    self.logger.warning(self.i18n.get('WARN_INVALID_NUMBER'))
            except KeyboardInterrupt:
                if self.logger:
                    self.logger.info(self.i18n.get('INFO_EXIT_INTERRUPT'))
                exit(0)

    def get_context_info(self):
        """Obtener información de contexto para el manejo de excepciones o UI"""
        return {
            "app_version": "1.3.0",
            "config_loaded": bool(self.config),
            "max_dimensions": f"{getattr(self, 'max_width_mm', 'N/A')}x{getattr(self, 'max_height_mm', 'N/A')}mm"
        }

    def input_with_label(self, prompt):
        " Imprime un prompt de entrada con etiqueta. "
        return input(f"[INPUT] {prompt}")

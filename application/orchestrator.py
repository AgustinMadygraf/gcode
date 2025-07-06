"""
application/orchestrator.py
Orquestador principal de la aplicación. Separa la lógica de orquestación de la UI.
"""

import os
from adapters.input.svg_file_selector_adapter import _find_svg_files_recursively

class ApplicationOrchestrator:
    " Orquestador principal de la aplicación SVG2GCODE. "
    def __init__(
        self,
        container,
        presenter,
        services,
        mode_strategy,
        args=None
    ):
        self.container = container
        self.presenter = presenter
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
            self.logger.info(self.presenter.i18n.get('INFO_STARTING_MODE'))
        # Delegar la ejecución al modo de operación (interactivo/no-interactivo)
        result = self.mode_strategy.run(self)
        if self.logger:
            self.logger.info(self.presenter.i18n.get('INFO_EXECUTION_FINISHED'))
        return result

    # Métodos para exponer operaciones a la UI (pueden expandirse según necesidades)
    def configure_write_area(self):
        """Permite al usuario seleccionar un preset de superficie o ingresar dimensiones personalizadas."""
        presets = self.config.get("SURFACE_PRESETS", {})
        plotter_max_area = self.config.plotter_max_area_mm
        dims, preset_name = self.presenter.prompt_surface_preset(presets, plotter_max_area)
        if hasattr(self.config, 'set_target_write_area_mm'):
            self.config.set_target_write_area_mm(dims)
        else:
            self.config.TARGET_WRITE_AREA_MM = dims
        self.presenter.print_success(self.presenter.i18n.get('SUCCESS_AREA_CONFIGURED', dims0=dims[0], dims1=dims[1], preset_name=preset_name))
        if self.logger:
            self.logger.info(self.presenter.i18n.get('SUCCESS_AREA_CONFIGURED', dims0=dims[0], dims1=dims[1], preset_name=preset_name))

    def select_operation_mode(self):
        " Selecciona el modo de operación de la aplicación (interactivo/no-interactivo). "
        args = self.args
        exit_keywords = {'salir', 'exit', 'quit'}
        if self.logger:
            self.logger.debug(self.presenter.i18n.get('DEBUG_SELECTING_MODE'))
        # 1. Si modo batch/no-interactive, omitir menú
        if args and getattr(args, 'no_interactive', False):
            if self.logger:
                self.logger.info(self.presenter.i18n.get('INFO_NON_INTERACTIVE_MODE'))
            return None
        # 2. Si hay input/output por argumento, saltar selección de archivos
        if args and getattr(args, 'input', None) and getattr(args, 'output', None):
            if self.logger:
                self.logger.info(self.presenter.i18n.get('INFO_DIRECT_EXECUTION'))
            self.presenter.print(self.presenter.i18n.get('INFO_DIRECT_EXECUTION'), color='cyan')
            return 1 if str(args.input).lower().endswith('.svg') else 2
        # 3. Si no hay archivos SVG/GCODE disponibles, menú reducido
        svg_dir = './data/svg_input'
        gcode_dir = './data/gcode_output'
        svg_files = []
        gcode_files = []
        try:
            svg_files = _find_svg_files_recursively(svg_dir)
        except ImportError:
            # El módulo no se pudo importar
            if self.logger:
                self.logger.warning(self.presenter.i18n.get('WARN_IMPORT_SVG_SELECTOR'))
        except FileNotFoundError:
            # El directorio de entrada no existe
            if self.logger:
                self.logger.warning(self.presenter.i18n.get('WARN_DIR_NOT_EXISTS', svg_dir=svg_dir))
        except OSError as e:
            # Otro error relacionado con el sistema de archivos
            if self.logger:
                self.logger.warning(self.presenter.i18n.get('WARN_FS_ERROR', error=str(e)))
        try:
            gcode_files = [f for f in os.listdir(gcode_dir) if f.lower().endswith('.gcode')]
        except (FileNotFoundError, OSError):
            pass
        if not svg_files and not gcode_files:
            if self.logger:
                self.logger.warning(self.presenter.i18n.get('WARN_NO_FILES_FOUND'))
            self.presenter.print(self.presenter.i18n.get('WARN_NO_FILES_FOUND'), color='yellow')
            self.presenter.print(self.presenter.i18n.get('INFO_OPTIONS'), color='bold')
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_CHANGE_INPUT_DIR'))
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_EXIT'))
            while True:
                user_input = self.presenter.input(self.presenter.i18n.get('PROMPT_SELECT_OPTION'))
                if user_input.strip() in {'0', 'salir', 'exit', 'quit'}:
                    self.presenter.print(self.presenter.i18n.get('INFO_EXIT'), color='yellow')
                    if self.logger:
                        self.logger.info(self.presenter.i18n.get('INFO_USER_EXIT_REDUCED'))
                    exit(0)
                elif user_input.strip() == '1':
                    self.presenter.print(self.presenter.i18n.get('WARN_NOT_IMPLEMENTED'), color='yellow')
                    if self.logger:
                        self.logger.warning(self.presenter.i18n.get('WARN_NOT_IMPLEMENTED'))
                else:
                    self.presenter.print(self.presenter.i18n.get('WARN_INVALID_OPTION'), color='yellow')
                    if self.logger:
                        self.logger.warning(self.presenter.i18n.get('WARN_INVALID_OPTION'))
        # 4. Menú clásico por defecto
        if hasattr(self.presenter, 'select_operation_mode'):
            return self.presenter.select_operation_mode()
        # Fallback clásico
        while True:
            self.presenter.print(self.presenter.i18n.get('MENU_MAIN_TITLE'), color='bold')
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_CONVERT'))
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_OPTIMIZE'))
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_CONFIGURE_AREA'))
            try:
                user_input = self.presenter.input(self.presenter.i18n.get('PROMPT_SELECT_OPTION'))
                if user_input.strip().lower() in exit_keywords:
                    self.presenter.print(self.presenter.i18n.get('INFO_EXIT'), color='yellow')
                    if self.logger:
                        self.logger.info(self.presenter.i18n.get('INFO_USER_EXIT_MAIN'))
                    exit(0)
                choice = int(user_input)
                if choice in [1, 2]:
                    if self.logger:
                        self.logger.debug(self.presenter.i18n.get('DEBUG_USER_SELECTED_OP', choice=choice))
                    return choice
                elif choice == 3:
                    self.configure_write_area()
                else:
                    self.presenter.print(self.presenter.i18n.get('WARN_INVALID_SELECTION'), color='yellow')
                    if self.logger:
                        self.logger.warning(self.presenter.i18n.get('WARN_INVALID_SELECTION'))
            except ValueError:
                self.presenter.print(self.presenter.i18n.get('WARN_INVALID_NUMBER'), color='yellow')
                if self.logger:
                    self.logger.warning(self.presenter.i18n.get('WARN_INVALID_NUMBER'))
            except KeyboardInterrupt:
                self.presenter.print(self.presenter.i18n.get('INFO_EXIT_INTERRUPT'), color='yellow')
                if self.logger:
                    self.logger.info(self.presenter.i18n.get('INFO_EXIT_INTERRUPT'))
                exit(0)

    def _get_context_info(self):
        """Obtener información de contexto para el manejo de excepciones o UI"""
        return {
            "app_version": "1.3.0",
            "config_loaded": bool(self.config),
            "max_dimensions": f"{getattr(self, 'max_width_mm', 'N/A')}x{getattr(self, 'max_height_mm', 'N/A')}mm"
        }

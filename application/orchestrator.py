"""
application/orchestrator.py
Orquestador principal de la aplicación. Separa la lógica de orquestación de la UI.
"""

import os

class ApplicationOrchestrator:
    def __init__(self, container, presenter, filename_service, config, event_bus, workflows, operations, mode_strategy, args=None):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config
        self.event_bus = event_bus
        self.workflows = workflows
        self.operations = operations
        self.mode_strategy = mode_strategy
        self.args = args

    def run(self):
        # Delegar la ejecución al modo de operación (interactivo/no-interactivo)
        return self.mode_strategy.run(self)

    # Métodos para exponer operaciones a la UI (pueden expandirse según necesidades)
    def get_operation(self, op_id):
        return self.operations.get(op_id)

    # Métodos de UI requeridos por estrategias de modo
    def select_operation_mode(self):
        # Adaptación de menú según contexto avanzado
        args = self.args
        exit_keywords = {'salir', 'exit', 'quit'}
        # 1. Si modo batch/no-interactive, omitir menú
        if args and getattr(args, 'no_interactive', False):
            return None  # El modo ya se maneja en la estrategia
        # 2. Si hay input/output por argumento, saltar selección de archivos
        if args and getattr(args, 'input', None) and getattr(args, 'output', None):
            self.presenter.print(self.presenter.i18n.get('INFO_DIRECT_EXECUTION'), color='cyan')
            return 1 if str(args.input).lower().endswith('.svg') else 2
        # 3. Si no hay archivos SVG/GCODE disponibles, menú reducido
        svg_dir = './data/svg_input'
        gcode_dir = './data/gcode_output'
        svg_files = []
        gcode_files = []
        try:
            from adapters.input.svg_file_selector_adapter import _find_svg_files_recursively
            svg_files = _find_svg_files_recursively(svg_dir)
        except Exception:
            pass
        try:
            gcode_files = [f for f in os.listdir(gcode_dir) if f.lower().endswith('.gcode')]
        except Exception:
            pass
        if not svg_files and not gcode_files:
            self.presenter.print(self.presenter.i18n.get('WARN_NO_FILES_FOUND'), color='yellow')
            self.presenter.print(self.presenter.i18n.get('INFO_OPTIONS'), color='bold')
            self.presenter.print_option('1) Cambiar carpeta de entrada')
            self.presenter.print_option('0) Salir')
            while True:
                user_input = self.presenter.input(self.presenter.i18n.get('PROMPT_SELECT_OPTION'))
                if user_input.strip() in {'0', 'salir', 'exit', 'quit'}:
                    self.presenter.print(self.presenter.i18n.get('INFO_EXIT'), color='yellow')
                    exit(0)
                elif user_input.strip() == '1':
                    self.presenter.print(self.presenter.i18n.get('WARN_NOT_IMPLEMENTED'), color='yellow')
                else:
                    self.presenter.print(self.presenter.i18n.get('WARN_INVALID_OPTION'), color='yellow')
        # 4. Menú clásico por defecto
        if hasattr(self.presenter, 'select_operation_mode'):
            return self.presenter.select_operation_mode()
        # Fallback clásico
        while True:
            self.presenter.print(self.presenter.i18n.get('MENU_MAIN_TITLE'), color='bold')
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_CONVERT'))
            self.presenter.print_option(self.presenter.i18n.get('MENU_OPTION_OPTIMIZE'))
            try:
                user_input = self.presenter.input(self.presenter.i18n.get('PROMPT_SELECT_OPTION'))
                if user_input.strip().lower() in exit_keywords:
                    self.presenter.print(self.presenter.i18n.get('INFO_EXIT'), color='yellow')
                    exit(0)
                choice = int(user_input)
                if choice in [1, 2]:
                    return choice
                self.presenter.print(self.presenter.i18n.get('WARN_INVALID_SELECTION'), color='yellow')
            except ValueError:
                self.presenter.print(self.presenter.i18n.get('WARN_INVALID_NUMBER'), color='yellow')
            except KeyboardInterrupt:
                self.presenter.print(self.presenter.i18n.get('INFO_EXIT_INTERRUPT'), color='yellow')
                exit(0)

    def _get_context_info(self):
        """Obtener información de contexto para el manejo de excepciones o UI"""
        return {
            "app_version": "1.3.0",
            "config_loaded": bool(self.config),
            "max_dimensions": f"{getattr(self, 'max_width_mm', 'N/A')}x{getattr(self, 'max_height_mm', 'N/A')}mm"
        }

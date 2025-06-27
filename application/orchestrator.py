"""
application/orchestrator.py
Orquestador principal de la aplicación. Separa la lógica de orquestación de la UI.
"""

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
        # Delegar en el presentador o lógica de UI
        if hasattr(self.presenter, 'select_operation_mode'):
            return self.presenter.select_operation_mode()
        # Fallback: lógica mínima
        self.presenter.print('menu_title', color='bold')
        self.presenter.print('option_svg_to_gcode')
        self.presenter.print('option_optimize')
        exit_keywords = {'salir', 'exit', 'quit'}
        while True:
            try:
                user_input = self.presenter.input('Ingrese el número de opción: ')
                if user_input.strip().lower() in exit_keywords:
                    self.presenter.print('\nSaliendo del programa. ¡Hasta luego!', color='yellow')
                    exit(0)
                choice = int(user_input)
                if choice in [1, 2]:
                    return choice
                self.presenter.print('invalid_selection', color='yellow')
            except ValueError:
                self.presenter.print('invalid_number', color='yellow')
            except KeyboardInterrupt:
                self.presenter.print('\nSaliendo del programa por interrupción (Ctrl+C).', color='yellow')
                exit(0)

    def _get_context_info(self):
        """Obtener información de contexto para el manejo de excepciones o UI"""
        return {
            "app_version": "1.3.0",
            "config_loaded": bool(self.config),
            "max_dimensions": f"{getattr(self, 'max_width_mm', 'N/A')}x{getattr(self, 'max_height_mm', 'N/A')}mm"
        }

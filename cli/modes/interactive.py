"""
Estrategia para el modo interactivo.
"""
from .base import ModeStrategy

class InteractiveModeStrategy(ModeStrategy):
    def run(self, app):
        error_handler = app.container.error_handler
        exit_keywords = {None, 0, '0', 'salir', 'exit', 'quit', 'SALIR', 'EXIT', 'QUIT'}
        while True:
            operation_mode = app.orchestrator.select_operation_mode()
            if (isinstance(operation_mode, str) and operation_mode.strip().lower() in {'0', 'salir', 'exit', 'quit'}) or \
               (isinstance(operation_mode, int) and operation_mode == 0) or \
               (operation_mode is None):
                app.presenter.print(app.i18n.get("INFO_EXIT"), color='yellow')
                break
            operation = app.operations.get(operation_mode)
            if operation:
                result = error_handler.wrap_execution(
                    operation.execute,
                    app.orchestrator._get_context_info()
                )
                if not result.get('success', False):
                    error_info = result.get('message', app.i18n.get('ERROR_GENERIC'))
                    error_type = result.get('error', 'Error')
                    app.presenter.print(f"[{error_type.upper()}] {error_info}", color='red')
            else:
                app.presenter.print(app.i18n.get("ERROR_INVALID_SELECTION"), color='yellow')
        return 0

"""
Estrategia para el modo interactivo.
"""
from .base import ModeStrategy

class InteractiveModeStrategy(ModeStrategy):
    def run(self, app):
        error_handler = app.container.error_handler
        operation_mode = app.orchestrator.select_operation_mode()
        operation = app.operations.get(operation_mode)
        if operation:
            result = error_handler.wrap_execution(
                operation.execute,
                app.orchestrator._get_context_info()
            )
        else:
            app.presenter.print(app.i18n.get("ERROR_INVALID_SELECTION"), color='yellow')
            return 1
        if not result.get('success', False):
            error_info = result.get('message', app.i18n.get('ERROR_GENERIC'))
            error_type = result.get('error', 'Error')
            app.presenter.print(f"[{error_type.upper()}] {error_info}", color='red')
            return 1
        return 0

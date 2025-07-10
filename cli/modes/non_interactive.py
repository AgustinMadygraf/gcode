"""
Estrategia para el modo no interactivo.
"""
from cli.modes.base import ModeStrategy

class NonInteractiveModeStrategy(ModeStrategy):
    " Estrategia para el modo no interactivo. "
    def run(self, app):
        " Ejecuta el modo no interactivo. "
        return app.non_interactive_workflow.run(app.args)

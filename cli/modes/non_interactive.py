"""
Estrategia para el modo no interactivo.
"""
from .base import ModeStrategy

class NonInteractiveModeStrategy(ModeStrategy):
    def run(self, app):
        return app.non_interactive_workflow.run(app.args)

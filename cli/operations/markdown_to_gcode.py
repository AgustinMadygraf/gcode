"""
Operación CLI para Markdown → GCODE
"""
class MarkdownToGcodeOperation:
    " Operación para convertir Markdown a GCODE. "
    def __init__(self, workflow, config):
        self.workflow = workflow
        self.config = config

    def run(self, input_path, output_path=None):
        " Ejecuta la conversión de Markdown a GCODE. "
        return self.workflow.run(input_path, output_path)

"""
Workflow para el modo no interactivo de generación de G-code desde SVG.
"""

from application.workflows.input_handler import InputHandler
from application.workflows.processing_strategies import SvgProcessingStrategy, GcodeProcessingStrategy

class NonInteractiveSvgToGcodeWorkflow:
    " Flujo de trabajo no interactivo para convertir SVG a G-code. "
    def write_gcode_file(self, gcode_lines, output_path):
        """Método dummy para compatibilidad con flujos que lo requieran."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(gcode_lines))
    def __init__(self, container, presenter, filename_service, config,
                 svg_strategy=None, gcode_strategy=None, input_handler=None):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config
        self.logger = container.logger
        self.svg_strategy = svg_strategy or SvgProcessingStrategy()
        self.gcode_strategy = gcode_strategy or GcodeProcessingStrategy()
        self.input_handler = input_handler or InputHandler(self.presenter)

    def run(self, args):
        " Ejecuta el flujo de trabajo no interactivo de SVG a G-code. "
        input_type, input_data, temp_path = self.input_handler.read(args)
        if input_type is None:
            return 2
        output_path = args.output
        optimize = getattr(args, 'optimize', False)
        rescale = getattr(args, 'rescale', None)
        # --- Estrategia de procesamiento ---
        if input_type == 'svg':
            strategy = self.svg_strategy
        elif input_type == 'gcode':
            strategy = self.gcode_strategy
        else:
            self.presenter.print("error_occurred", color='red')
            return 3
        return strategy.process(self, args, input_data, temp_path, output_path, optimize, rescale)

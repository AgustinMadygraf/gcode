"""
Workflow para el modo no interactivo de generación de G-code desde SVG.
"""

from pathlib import Path
import sys
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from application.use_cases.gcode_to_gcode_use_case import GcodeToGcodeUseCase
from application.use_cases.gcode_rescale_use_case import GcodeRescaleUseCase
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
from domain.services.path_transform_strategies import MirrorVerticalStrategy
from application.workflows.input_handler import InputHandler
from application.workflows.processing_strategies import SvgProcessingStrategy, GcodeProcessingStrategy

class NonInteractiveSvgToGcodeWorkflow:
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

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))

    def run(self, args):
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

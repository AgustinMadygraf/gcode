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

class NonInteractiveSvgToGcodeWorkflow:
    def __init__(self, container, presenter, filename_service, config):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config
        self.logger = container.logger

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))

    def run(self, args):
        if not args or not args.input:
            self.presenter.print("error_file_not_found", color='red')
            return 2
        input_path = args.input
        output_path = args.output
        optimize = getattr(args, 'optimize', False)
        rescale = getattr(args, 'rescale', None)
        # Leer entrada desde stdin si input es '-'
        if input_path == '-':
            input_data = sys.stdin.read()
            # Detectar tipo de entrada por flag o contenido
            if optimize or rescale or (args.input and str(args.input).lower().endswith('.gcode')):
                # Procesar como G-code
                gcode_lines = input_data.splitlines()
                if optimize:
                    refactor_use_case = GcodeToGcodeUseCase(
                        filename_service=self.filename_service,
                        logger=self.logger
                    )
                    # Guardar temporalmente para reutilizar el flujo existente
                    from tempfile import NamedTemporaryFile
                    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.gcode') as tmp:
                        tmp.write(input_data)
                        tmp_path = tmp.name
                    result = refactor_use_case.execute(Path(tmp_path))
                    gcode_out = open(result['output_file'], encoding='utf-8').read().splitlines()
                    if output_path == '-' or output_path is None:
                        sys.stdout.write("\n".join(gcode_out) + "\n")
                        return 0
                    else:
                        self._write_gcode_file(Path(output_path), gcode_out)
                        return 0
                elif rescale:
                    rescale_use_case = GcodeRescaleUseCase(
                        filename_service=self.filename_service,
                        logger=self.logger,
                        config_provider=self.config
                    )
                    from tempfile import NamedTemporaryFile
                    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.gcode') as tmp:
                        tmp.write(input_data)
                        tmp_path = tmp.name
                    result = rescale_use_case.execute(Path(tmp_path), rescale)
                    gcode_out = open(result['output_file'], encoding='utf-8').read().splitlines()
                    if output_path == '-' or output_path is None:
                        sys.stdout.write("\n".join(gcode_out) + "\n")
                        return 0
                    else:
                        self._write_gcode_file(Path(output_path), gcode_out)
                        return 0
                else:
                    self.presenter.print("error_occurred", color='red')
                    return 3
            else:
                # Procesar como SVG
                from tempfile import NamedTemporaryFile
                with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.svg') as tmp:
                    tmp.write(input_data)
                    tmp_path = tmp.name
                svg_loader_factory = self.container.get_svg_loader
                self.presenter.print("processing_start", color='blue')
                result = SvgToGcodeUseCase(
                    svg_loader_factory=svg_loader_factory,
                    path_processing_service=PathProcessingService(
                        min_length=1e-3,
                        remove_svg_border=self.config.get_remove_svg_border(),
                        border_tolerance=self.config.get_border_detection_tolerance()
                    ),
                    gcode_generation_service=GCodeGenerationService(self.container.get_gcode_generator()),
                    gcode_compression_use_case=CompressGcodeUseCase(
                        create_gcode_compression_service(logger=self.logger),
                        AdapterFactory.create_config_adapter(self.config)
                    ),
                    logger=self.logger,
                    filename_service=self.filename_service
                ).execute(Path(tmp_path))
                gcode_lines = result['compressed_gcode'] if optimize else result['gcode_lines']
                if output_path == '-' or output_path is None:
                    sys.stdout.write("\n".join(gcode_lines) + "\n")
                    return 0
                else:
                    self._write_gcode_file(Path(output_path), gcode_lines)
                    return 0
        # Si input_path no es '-', seguir flujo normal
        # SVG a GCODE
        if str(input_path).lower().endswith('.svg'):
            svg_loader_factory = self.container.get_svg_loader
            self.presenter.print("processing_start", color='blue')
            paths = svg_loader_factory(input_path).get_paths()
            self.presenter.print("processing_complete", color='green')
            bbox = DomainFactory.create_geometry_service()._calculate_bbox(paths)
            _xmin, _xmax, _ymin, _ymax = bbox
            _cx, cy = DomainFactory.create_geometry_service()._center(bbox)
            transform_strategies = []
            if self.config.get_mirror_vertical():
                transform_strategies.append(MirrorVerticalStrategy(cy))
            path_processor = PathProcessingService(
                min_length=1e-3,
                remove_svg_border=self.config.get_remove_svg_border(),
                border_tolerance=self.config.get_border_detection_tolerance()
            )
            generator = self.container.get_gcode_generator(transform_strategies=transform_strategies)
            gcode_service = GCodeGenerationService(generator)
            compression_service = create_gcode_compression_service(logger=self.logger)
            config_reader = AdapterFactory.create_config_adapter(self.config)
            compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
            svg_to_gcode_use_case = SvgToGcodeUseCase(
                svg_loader_factory=svg_loader_factory,
                path_processing_service=path_processor,
                gcode_generation_service=gcode_service,
                gcode_compression_use_case=compress_use_case,
                logger=self.logger,
                filename_service=self.filename_service
            )
            # --- Contexto de herramienta desde argumentos CLI ---
            tool_type = getattr(args, 'tool', 'pen')
            double_pass = getattr(args, 'double_pass', True)
            context = {
                "tool_type": tool_type,
                "double_pass": double_pass
            }
            result = svg_to_gcode_use_case.execute(input_path, transform_strategies=transform_strategies, context=context)
            gcode_lines = result['compressed_gcode'] if optimize else result['gcode_lines']
            if output_path == '-' or output_path is None:
                sys.stdout.write("\n".join(gcode_lines) + "\n")
                return 0
            else:
                self._write_gcode_file(Path(output_path), gcode_lines)
                out_file = output_path
                self.presenter.print("processing_complete", color='green')
                self.presenter.print("success_refactor", color='green', output_file=out_file)
                return 0
        # GCODE a GCODE
        elif str(input_path).lower().endswith('.gcode'):
            if optimize:
                refactor_use_case = GcodeToGcodeUseCase(
                    filename_service=self.filename_service,
                    logger=self.logger
                )
                result = refactor_use_case.execute(input_path)
                gcode_out = open(result['output_file'], encoding='utf-8').read().splitlines()
                if output_path == '-' or output_path is None:
                    sys.stdout.write("\n".join(gcode_out) + "\n")
                    return 0
                else:
                    self._write_gcode_file(Path(output_path), gcode_out)
                    out_file = output_path
                    self.presenter.print("success_refactor", color='green', output_file=out_file)
                    self.presenter.print("success_optimize", color='green', changes=result['changes_made'])
                    return 0
            elif rescale:
                rescale_use_case = GcodeRescaleUseCase(
                    filename_service=self.filename_service,
                    logger=self.logger,
                    config_provider=self.config
                )
                result = rescale_use_case.execute(input_path, rescale)
                gcode_out = open(result['output_file'], encoding='utf-8').read().splitlines()
                if output_path == '-' or output_path is None:
                    sys.stdout.write("\n".join(gcode_out) + "\n")
                    return 0
                else:
                    self._write_gcode_file(Path(output_path), gcode_out)
                    out_file = output_path
                    original_dim = result.get('original_dimensions', {})
                    new_dim = result.get('new_dimensions', {})
                    self.presenter.print("success_rescale", color='green', output_file=out_file)
                    self.presenter.print("rescale_original", width=original_dim.get('width', 0), height=original_dim.get('height', 0))
                    self.presenter.print("rescale_new", width=new_dim.get('width', 0), height=new_dim.get('height', 0))
                    self.presenter.print("rescale_factor", factor=result.get('scale_factor', 1.0))
                    self.presenter.print("rescale_cmds", g0g1=result['commands_rescaled']['g0g1'], g2g3=result['commands_rescaled']['g2g3'])
                    return 0
        else:
            self.presenter.print("error_occurred", color='red')
            return 3

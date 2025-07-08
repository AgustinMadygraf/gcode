"""
Workflow para SVG a GCODE.
Orquesta el proceso de conversión, delegando a casos de uso y servicios.
"""
from pathlib import Path
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.performance.timing import PerformanceTimer
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from domain.services.path_transform_strategies import MirrorVerticalStrategy

class SvgToGcodeWorkflow:
    " Workflow para convertir SVG a GCODE. "
    DEBUG_ENABLED = False  # Controla si los logs debug están activos para esta clase

    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED and self.logger:
            self.logger.debug(msg, *args, **kwargs)

    def __init__(self, container, presenter, filename_service, config):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config
        self.i18n = presenter.i18n
        self.logger = getattr(container, 'logger', None)

    def run(self, selector=None):
        " Ejecuta el flujo de trabajo. "
        self._debug(self.i18n.get("debug_workflow_started"))
        with PerformanceTimer.measure(self.logger, "SVG to GCODE Workflow"):  # Medición de tiempo
            # Si el selector no tiene i18n, se lo inyecta (retrocompatibilidad)
            if selector and getattr(selector, 'i18n', None) is None:
                self._debug(self.i18n.get("debug_selector_no_i18n"))
                selector.i18n = self.presenter.i18n
            svg_file = selector.select_svg_file()
            if not svg_file:
                self.logger.warning(self.i18n.get("warn_no_svg_selected"))
                self.logger.error(self.i18n.get("error_no_svg"))
                return False
            svg_file = Path(svg_file)
            svg_file_str = str(svg_file).replace('\\', '/')
            self.logger.info(self.i18n.get("INFO_SVG_SELECTED", filename=svg_file_str))
            gcode_file = self.filename_service.next_filename(svg_file)
            gcode_file_str = str(gcode_file).replace('\\', '/')
            self._debug(self.i18n.get("INFO_GCODE_OUTPUT", filename=gcode_file_str))
            svg_loader_factory = self.container.get_svg_loader
            self._debug(self.i18n.get("INFO_PROCESSING_FILE"))
            try:
                paths = svg_loader_factory(svg_file).get_paths()
                self._debug(self.i18n.get("debug_svg_paths_extracted", count=len(paths) if paths else 0))
            except (OSError, ValueError) as e:
                self.logger.error(self.i18n.get("error_loading_svg_paths", error=str(e)))
                self.logger.error(self.i18n.get("error_no_svg"))
                return False
            self._debug(self.i18n.get("INFO_PROCESSING_DONE"))
            if not paths or len(paths) == 0:
                self.logger.warning(self.i18n.get("warn_svg_no_valid_paths", filename=svg_file_str))
            if paths and len(paths) > 1:
                self._debug(self.i18n.get("processing_paths"))
            try:
                geometry_service = DomainFactory.create_geometry_service()
                if hasattr(geometry_service, "calculate_bbox"):
                    bbox = geometry_service.calculate_bbox(paths)
                else:
                    self.logger.error(self.i18n.get("error_no_calculate_bbox"))
                    raise AttributeError(self.i18n.get("error_no_calculate_bbox"))
                self._debug(self.i18n.get("debug_bbox_calculated", bbox=str(bbox)))
            except (AttributeError, ValueError) as e:
                self.logger.warning(self.i18n.get("warn_bbox_failed", error=str(e)))
                bbox = (0, 0, 0, 0)
            try:
                _xmin, _xmax, _ymin, _ymax = bbox
                geometry_service = DomainFactory.create_geometry_service()
                if hasattr(geometry_service, "center"):
                    _cx, cy = geometry_service.center(bbox)
                else:
                    self.logger.error(self.i18n.get("error_no_center_method"))
                    raise AttributeError(self.i18n.get("error_no_center_method"))
                self._debug(self.i18n.get("debug_center_calculated", cx=_cx, cy=cy))
            except (AttributeError, ValueError, TypeError) as e:
                self.logger.warning(self.i18n.get("warn_center_failed", error=str(e)))
                cy = 0
            transform_strategies = []
            if self.config.get_mirror_vertical():
                transform_strategies.append(MirrorVerticalStrategy(cy))
                self._debug(self.i18n.get("debug_vertical_mirror_applied"))
            path_processor = PathProcessingService(
                min_length=1e-3,
                remove_svg_border=self.config.get_remove_svg_border(),
                border_tolerance=self.config.get_border_detection_tolerance(),
                logger=self.logger,
                i18n=self.i18n
            )
            self._debug(self.i18n.get(
                "debug_path_processor_configured",
                min_length=1e-3,
                remove_svg_border=self.config.get_remove_svg_border(),
                border_tolerance=self.config.get_border_detection_tolerance()
            ))
            generator = self.container.get_gcode_generator(
                transform_strategies=transform_strategies,
                i18n=self.i18n
            )
            gcode_service = GCodeGenerationService(generator)
            compression_service = create_gcode_compression_service(logger=self.logger, i18n=self.i18n)
            config_reader = AdapterFactory.create_config_adapter(self.config)
            compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
            svg_to_gcode_use_case = SvgToGcodeUseCase(
                svg_loader_factory=svg_loader_factory,
                path_processing_service=path_processor,
                gcode_generation_service=gcode_service,
                gcode_compression_use_case=compress_use_case,
                logger=self.logger,
                filename_service=self.filename_service,
                i18n=self.i18n
            )
            # --- Herramienta desde configuración ---
            tool_type_str = self.config.tool_type if hasattr(self.config, 'tool_type') else 'pen'
            double_pass = False
            if tool_type_str == "pen":
                double_pass = getattr(self.config, 'pen_double_pass', False)
                self._debug(self.i18n.get("debug_double_pass_configured", double_pass=double_pass))
            context = {
                "tool_type": tool_type_str,
                "double_pass": double_pass,
                "tool_diameter": getattr(self.config, 'tool_diameter', 0.4)
            }
            self._debug(self.i18n.get("debug_executing_svg_to_gcode_usecase"))
            try:
                result = svg_to_gcode_use_case.execute(svg_file, context=context)
            except (OSError, ValueError) as e:
                self.logger.error(self.i18n.get("error_svg_to_gcode_usecase", error=str(e)))
                self.logger.error(self.i18n.get("error_no_svg"))
                return False
            gcode_lines = result['compressed_gcode']
            total_lines = len(gcode_lines)
            for i, _ in enumerate(gcode_lines, 1):
                if i % max(1, total_lines // 100) == 0 or i == total_lines:
                    if i % max(1, total_lines // 10) == 0 or i == total_lines:
                        self._debug(self.i18n.get("debug_gcode_write_progress_simple", current=i, total=total_lines))
            try:
                with gcode_file.open("w", encoding="utf-8") as f:
                    f.write("\n".join(gcode_lines))
                self._debug(self.i18n.get("INFO_GCODE_WRITTEN", filename=gcode_file_str))
            except (OSError, IOError) as e:
                self.logger.error(self.i18n.get("error_gcode_write", error=str(e)))
                self.logger.error(self.i18n.get("error_no_svg"))
                return False
            # Separador visual antes de logs técnicos si modo dev
            self.container.event_bus.publish(
                'gcode_generated',
                {
                    'svg_file': svg_file_str,
                    'gcode_file': gcode_file_str
                }
            )
            self.logger.info(self.i18n.get("INFO_GCODE_SUCCESS", filename=gcode_file_str))
            self._debug(self.i18n.get("info_workflow_completed"))
            return True

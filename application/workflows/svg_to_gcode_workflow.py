"""
Workflow para SVG a GCODE.
Orquesta el proceso de conversión, delegando a casos de uso y servicios.
"""
from pathlib import Path
import re

from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.performance.timing import PerformanceTimer
from infrastructure.logger_helper import LoggerHelper
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from domain.services.path_transform_strategies import VerticalFlipStrategy
from utils.gcode_offset import calcular_offset_y, aplicar_offset_y_a_gcode


class SvgToGcodeWorkflow(LoggerHelper):
    " Workflow para convertir SVG a GCODE. "

    def __init__(self, container, presenter, filename_service, config, offset_x=None, offset_y=None, center=False):
        super().__init__()
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.center = center
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config
        self.i18n = presenter.i18n
        self.logger = getattr(container, 'logger', None)

    def run(self, selector=None):
        " Ejecuta el flujo de trabajo. "
        self._debug(self.i18n.get("debug_workflow_started"))
        perf_timer = PerformanceTimer(container=self.container, config=self.config)
        with perf_timer.measure("SVG to GCODE Workflow"):
            # Si el selector no tiene i18n, se lo inyecta (retrocompatibilidad)
            if selector and getattr(selector, 'i18n', None) is None:
                self._debug(self.i18n.get("debug_selector_no_i18n"))
                selector.i18n = self.presenter.i18n
            svg_file = selector.select_svg_file()
            if not svg_file:
                self.logger.warning(self.i18n.get("warn_no_svg_selected"))
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
            if self.config.get_flip_vertical():
                transform_strategies.append(VerticalFlipStrategy(cy))
                self._debug(self.i18n.get("debug_vertical_flip_applied"))
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
                i18n=self.i18n,
                config=config_reader
            )
            # --- Herramienta desde configuración ---
            tool_type_str = self.config.tool_type if hasattr(self.config, 'tool_type') else 'pen'
            double_pass = False
            if tool_type_str == "pen":
                double_pass = getattr(self.config, 'pen_double_pass', False)
                self._debug(self.i18n.get("debug_double_pass_configured", double_pass=double_pass))
            # --- Offset y centrado ---
            area_w, area_h = self.config.target_write_area_mm
            _xmin, _xmax, _ymin, _ymax = bbox
            drawing_w = _xmax - _xmin
            drawing_h = _ymax - _ymin
            offset_x = self.offset_x
            offset_y = self.offset_y
            if self.center:
                offset_x = (area_w / 2) - (_xmin + drawing_w / 2)
                offset_y = (area_h / 2) - (_ymin + drawing_h / 2)
                self.logger.info(self.i18n.get("INFO_CENTERING_OFFSET", offset_x=offset_x, offset_y=offset_y))
            # Validación de desbordes
            if offset_x is not None and offset_y is not None:
                new_xmin = _xmin + offset_x
                new_xmax = _xmax + offset_x
                new_ymin = _ymin + offset_y
                new_ymax = _ymax + offset_y
                if new_xmin < 0 or new_xmax > area_w or new_ymin < 0 or new_ymax > area_h:
                    self.logger.warning(
                        self.i18n.get(
                            "WARN_OFFSET_OVERFLOW",
                            xmin=new_xmin,
                            xmax=new_xmax,
                            ymin=new_ymin,
                            ymax=new_ymax,
                            area_w=area_w,
                            area_h=area_h
                        )
                    )
                else:
                    self.logger.info(self.i18n.get("INFO_OFFSET_APPLIED", offset_x=offset_x, offset_y=offset_y))
            context = {
                "tool_type": tool_type_str,
                "double_pass": double_pass,
                "tool_diameter": getattr(self.config, 'tool_diameter', 0.4),
                "offset_x": offset_x,
                "offset_y": offset_y,
                "center": self.center
            }
            self._debug(self.i18n.get("debug_executing_svg_to_gcode_usecase"))
            try:
                result = svg_to_gcode_use_case.execute(svg_file, context=context)
            except (OSError, ValueError) as e:
                self.logger.error(self.i18n.get("error_svg_to_gcode_usecase", error=str(e)))
                self.logger.error(self.i18n.get("error_no_svg"))
                return False
            gcode_lines = result['compressed_gcode']
            plotter_max_area_mm = self.config.plotter_max_area_mm
            target_write_area_mm = self.config.target_write_area_mm
            rotate_90 = getattr(self.config, 'rotate_90_clockwise', False)
            self._debug(f"[DEBUG] ROTATE_90_CLOCKWISE: {rotate_90}")
            self._debug(f"[DEBUG] PLOTTER_MAX_AREA_MM: {plotter_max_area_mm}")
            self._debug(f"[DEBUG] TARGET_WRITE_AREA_MM: {target_write_area_mm}")
            offset_y = 0.0
            if rotate_90:
                offset_y = calcular_offset_y(plotter_max_area_mm, target_write_area_mm)
                self._debug(f"[DEBUG] Offset Y calculado: {offset_y}")
                gcode_lines = aplicar_offset_y_a_gcode(gcode_lines, offset_y)
                self._debug("[DEBUG] Offset Y aplicado a todas las líneas G-code.")

                # Validación de overflow en coordenadas Y
                y_min = None
                y_max = None
                for line in gcode_lines:
                    match = re.search(r'Y([\-\d\.]+)', line)
                    if match:
                        y_val = float(match.group(1))
                        if y_min is None or y_val < y_min:
                            y_min = y_val
                        if y_max is None or y_val > y_max:
                            y_max = y_val
                area_h = target_write_area_mm[1]
                plotter_h = plotter_max_area_mm[1]
                if y_min is not None and (y_min < 0 or y_max > plotter_h):
                    self.logger.warning(f"[WARN] Overflow Y detectado: y_min={y_min}, y_max={y_max}, límite plotter={plotter_h}")
                else:
                    self._debug(f"[DEBUG] Offset Y aplicado correctamente: y_min={y_min}, y_max={y_max}, límite plotter={plotter_h}")
            flip_vertical = getattr(self.config, 'flip_vertical', False)
            if flip_vertical:
                self._debug("[DEBUG] FLIP_VERTICAL está activo y afecta la transformación geométrica.")
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

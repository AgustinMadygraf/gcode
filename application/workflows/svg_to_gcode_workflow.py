"""
Workflow para SVG a GCODE.
Orquesta el proceso de conversión, delegando a casos de uso y servicios.
"""
from pathlib import Path
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
from infrastructure.factories.adapter_factory import AdapterFactory
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from domain.services.path_transform_strategies import MirrorVerticalStrategy

class SvgToGcodeWorkflow:
    " Workflow para convertir SVG a GCODE. "
    def __init__(self, container, presenter, filename_service, config):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config

    def run(self, selector=None):
        " Ejecuta el flujo de trabajo. "
        logger = self.container.logger
        logger.info("[SVG2GCODE] Workflow started.")
        # Si el selector no tiene i18n, se lo inyecta (retrocompatibilidad)
        if selector and getattr(selector, 'i18n', None) is None:
            logger.debug("Selector sin i18n, inyectando desde presenter.")
            selector.i18n = self.presenter.i18n
        svg_file = selector.select_svg_file()
        if not svg_file:
            logger.warning("No se seleccionó archivo SVG. Proceso abortado.")
            self.presenter.print(self.presenter.i18n.get("error_no_svg"), color='red')
            return False
        svg_file = Path(svg_file)
        svg_file_str = str(svg_file).replace('\\', '/')
        logger.info(f"SVG seleccionado: {svg_file_str}")
        self.presenter.print(self.presenter.i18n.get("INFO_SVG_SELECTED", filename=svg_file_str), color='green')
        gcode_file = self.filename_service.next_filename(svg_file)
        gcode_file_str = str(gcode_file).replace('\\', '/')
        logger.info(f"Archivo de salida GCODE: {gcode_file_str}")
        self.presenter.print(self.presenter.i18n.get("INFO_GCODE_OUTPUT", filename=gcode_file_str), color='green')
        svg_loader_factory = self.container.get_svg_loader
        self.presenter.print(self.presenter.i18n.get("INFO_PROCESSING_FILE"), color='green')
        logger.info(f"Procesando archivo SVG: {svg_file_str}")
        try:
            paths = svg_loader_factory(svg_file).get_paths()
            logger.debug(f"Paths extraídos del SVG: {len(paths) if paths else 0}")
        except (OSError, ValueError) as e:
            logger.error(f"Error al cargar paths del SVG: {e}")
            self.presenter.print(self.presenter.i18n.get("error_no_svg"), color='red')
            return False
        self.presenter.print(self.presenter.i18n.get("INFO_PROCESSING_DONE"), color='green')
        if not paths or len(paths) == 0:
            logger.warning(f"El archivo SVG no contiene paths válidos: {svg_file_str}")
        if paths and len(paths) > 1:
            self.presenter.print_progress(len(paths), len(paths), prefix=self.presenter.i18n.get("processing_paths"))
        try:
            geometry_service = DomainFactory.create_geometry_service()
            if hasattr(geometry_service, "calculate_bbox"):
                bbox = geometry_service.calculate_bbox(paths)
            else:
                logger.error("El servicio de geometría no tiene el método público 'calculate_bbox'.")
                raise AttributeError("El servicio de geometría no tiene el método público 'calculate_bbox'.")
            logger.debug(f"BBox calculado: {bbox}")
        except (AttributeError, ValueError) as e:
            logger.warning(f"No se pudo calcular el bbox: {e}")
            bbox = (0, 0, 0, 0)
        try:
            _xmin, _xmax, _ymin, _ymax = bbox
            geometry_service = DomainFactory.create_geometry_service()
            if hasattr(geometry_service, "center"):
                _cx, cy = geometry_service.center(bbox)
            else:
                logger.error("El servicio de geometría no tiene el método público 'center'.")
                raise AttributeError("El servicio de geometría no tiene el método público 'center'.")
            logger.debug(f"Centro calculado: ({_cx}, {cy})")
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"No se pudo calcular el centro del bbox: {e}")
            cy = 0
        transform_strategies = []
        if self.config.get_mirror_vertical():
            transform_strategies.append(MirrorVerticalStrategy(cy))
            logger.info("Estrategia de espejo vertical aplicada.")
        path_processor = PathProcessingService(
            min_length=1e-3,
            remove_svg_border=self.config.get_remove_svg_border(),
            border_tolerance=self.config.get_border_detection_tolerance()
        )
        logger.debug(
            (
                "PathProcessor configurado: min_length=1e-3, "
                f"remove_svg_border={self.config.get_remove_svg_border()}, "
                f"border_tolerance={self.config.get_border_detection_tolerance()}"
            )
        )
        generator = self.container.get_gcode_generator(
            transform_strategies=transform_strategies,
            i18n=self.presenter.i18n
        )
        gcode_service = GCodeGenerationService(generator)
        compression_service = create_gcode_compression_service(logger=logger)
        config_reader = AdapterFactory.create_config_adapter(self.config)
        compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
        svg_to_gcode_use_case = SvgToGcodeUseCase(
            svg_loader_factory=svg_loader_factory,
            path_processing_service=path_processor,
            gcode_generation_service=gcode_service,
            gcode_compression_use_case=compress_use_case,
            logger=logger,
            filename_service=self.filename_service
        )
        # --- Selección de herramienta ---
        tool_type = self.presenter.prompt_selection(
            self.presenter.i18n.get("PROMPT_SELECT_TOOL"),
            options=[
                self.presenter.i18n.get("OPTION_TOOL_PEN"),
                self.presenter.i18n.get("OPTION_TOOL_MARKER")
            ]
        )
        tool_type_str = "pen" if tool_type == 1 else "marker"
        logger.info(f"Herramienta seleccionada: {tool_type_str}")
        double_pass = False
        if tool_type_str == "pen":
            double_pass = self.presenter.prompt_yes_no(
                self.presenter.i18n.get("PROMPT_DOUBLE_PASS"),
                default_yes=True
            )
            logger.debug(f"Doble pasada seleccionada: {double_pass}")
        context = {
            "tool_type": tool_type_str,
            "double_pass": double_pass
        }
        logger.info("Ejecutando caso de uso SvgToGcodeUseCase...")
        try:
            result = svg_to_gcode_use_case.execute(svg_file, context=context)
        except (OSError, ValueError) as e:
            logger.error(f"Error al ejecutar SvgToGcodeUseCase: {e}")
            self.presenter.print(self.presenter.i18n.get("error_no_svg"), color='red')
            return False
        gcode_lines = result['compressed_gcode']
        total_lines = len(gcode_lines)
        logger.info(f"Líneas de GCODE generadas: {total_lines}")
        for i, _ in enumerate(gcode_lines, 1):
            if i % max(1, total_lines // 100) == 0 or i == total_lines:
                self.presenter.print_progress(i, total_lines, prefix=self.presenter.i18n.get("generating_gcode"))
                if i % max(1, total_lines // 10) == 0 or i == total_lines:
                    logger.debug(f"Progreso de escritura de GCODE: {i}/{total_lines}")
        try:
            with gcode_file.open("w", encoding="utf-8") as f:
                f.write("\n".join(gcode_lines))
            logger.info(self.presenter.i18n.get("INFO_GCODE_WRITTEN", filename=gcode_file_str))
        except (OSError, IOError) as e:
            logger.error(f"Error al escribir el archivo GCODE: {e}")
            self.presenter.print(self.presenter.i18n.get("error_no_svg"), color='red')
            return False
        # Separador visual antes de logs técnicos si modo dev
        self.container.event_bus.publish('gcode_generated', {'svg_file': svg_file_str, 'gcode_file': gcode_file_str})
        self.presenter.print_success(self.presenter.i18n.get("INFO_GCODE_SUCCESS", filename=gcode_file_str))
        logger.info("[SVG2GCODE] Workflow finalizado correctamente.")
        print("\n")
        return True

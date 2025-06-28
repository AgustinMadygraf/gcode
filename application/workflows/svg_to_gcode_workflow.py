"""
Workflow para SVG a GCODE.
Orquesta el proceso de conversión, delegando a casos de uso y servicios.
"""
from pathlib import Path

class SvgToGcodeWorkflow:
    def __init__(self, container, presenter, filename_service, config):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config

    def run(self, selector):
        svg_file = selector.select_svg_file()
        if not svg_file:
            self.presenter.print(self.presenter.i18n.get("error_no_svg"), color='red')
            return False
        svg_file = Path(svg_file)
        svg_file_str = str(svg_file).replace('\\', '/')
        self.presenter.print(f"Archivo SVG seleccionado: {svg_file_str}" , color='blue')
        gcode_file = self.filename_service.next_filename(svg_file)
        gcode_file_str = str(gcode_file).replace('\\', '/')
        self.presenter.print(f"Archivo G-code de salida: {gcode_file_str}" , color='blue')
        svg_loader_factory = self.container.get_svg_loader
        self.presenter.print(self.presenter.i18n.get("processing_start"), color='blue')
        self.presenter.print(self.presenter.i18n.get("processing_complete"), color='green')
        paths = svg_loader_factory(svg_file).get_paths()
        def dummy_process(_):
            import time
            time.sleep(0.01)
        if paths and len(paths) > 1:
            self.presenter.print_progress(len(paths), len(paths), prefix=self.presenter.i18n.get("processing_paths"))
        try:
            from infrastructure.factories.domain_factory import DomainFactory
            bbox = DomainFactory.create_geometry_service()._calculate_bbox(paths)
        except (AttributeError, ValueError):
            bbox = (0, 0, 0, 0)
        _xmin, _xmax, _ymin, _ymax = bbox
        _cx, cy = DomainFactory.create_geometry_service()._center(bbox)
        transform_strategies = []
        if self.config.get_mirror_vertical():
            from domain.services.path_transform_strategies import MirrorVerticalStrategy
            transform_strategies.append(MirrorVerticalStrategy(cy))
        from application.use_cases.path_processing.path_processing_service import PathProcessingService
        path_processor = PathProcessingService(
            min_length=1e-3,
            remove_svg_border=self.config.get_remove_svg_border(),
            border_tolerance=self.config.get_border_detection_tolerance()
        )
        generator = self.container.get_gcode_generator(transform_strategies=transform_strategies)
        from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
        gcode_service = GCodeGenerationService(generator)
        from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
        compression_service = create_gcode_compression_service(logger=self.container.logger)
        from infrastructure.factories.adapter_factory import AdapterFactory
        config_reader = AdapterFactory.create_config_adapter(self.config)
        from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
        compress_use_case = CompressGcodeUseCase(compression_service, config_reader)
        from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
        svg_to_gcode_use_case = SvgToGcodeUseCase(
            svg_loader_factory=svg_loader_factory,
            path_processing_service=path_processor,
            gcode_generation_service=gcode_service,
            gcode_compression_use_case=compress_use_case,
            logger=self.container.logger,
            filename_service=self.filename_service
        )
        # --- Selección de herramienta ---
        tool_type = self.presenter.prompt_selection(
            self.presenter.i18n.get("tool_selection"),
            options=[
                self.presenter.i18n.get("tool_pen"),
                self.presenter.i18n.get("tool_marker")
            ]
        )
        tool_type_str = "pen" if tool_type == 1 else "marker"
        double_pass = False
        if tool_type_str == "pen":
            double_pass = self.presenter.prompt_yes_no(
                self.presenter.i18n.get("double_pass_question"),
                default_yes=True
            )
        context = {
            "tool_type": tool_type_str,
            "double_pass": double_pass
        }
        result = svg_to_gcode_use_case.execute(svg_file, transform_strategies=transform_strategies, context=context)
        gcode_lines = result['compressed_gcode']
        total_lines = len(gcode_lines)
        for i, _ in enumerate(gcode_lines, 1):
            if i % max(1, total_lines // 100) == 0 or i == total_lines:
                self.presenter.print_progress(i, total_lines, prefix=self.presenter.i18n.get("generating_gcode"))
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))
        # Separador visual antes de logs técnicos si modo dev
        if hasattr(self.container, 'logger') and getattr(self.container.logger, 'level', None) == 10:  # logging.DEBUG == 10
            self.presenter.print("\n--- [LOGS TÉCNICOS] ---\n", color='yellow')
        self.container.logger.info(f"Archivo G-code escrito: {gcode_file_str}")
        self.container.event_bus.publish('gcode_generated', {'svg_file': svg_file_str, 'gcode_file': gcode_file_str})
        self.presenter.print_success(f"✔ G-code generado exitosamente: {gcode_file_str}")
        return True

"""
Path: cli/main.py
Main CLI entry point for SVG to G-code conversion (OOP version).

Nota: Este módulo NO debe ejecutarse directamente. El único punto de entrada soportado es run.py
"""

from pathlib import Path
from infrastructure.config.config import Config
from adapters.input.config_adapter import ConfigAdapter
from domain.ports.config_port import ConfigPort
from domain.ports.config_provider import ConfigProviderPort
from domain.services.path_transform_strategies import MirrorVerticalStrategy
from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.gcode_compression.gcode_compression_service import GcodeCompressionService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from infrastructure.compressors.arc_compressor import ArcCompressor
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from adapters.input.path_sampler import PathSampler
from domain.services.geometry import GeometryService
from infrastructure.factories.container import Container
from domain.ports.logger_port import LoggerPort
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.infra_factory import InfraFactory
from application.exceptions import AppError, DomainError, InfrastructureError
from infrastructure.error_handling import ExceptionHandler
from domain.ports.file_selector_port import FileSelectorPort
from adapters.input.svg_file_selector_adapter import SvgFileSelectorAdapter
from adapters.input.gcode_file_selector_adapter import GcodeFileSelectorAdapter
from application.use_cases.gcode_to_gcode_use_case import GcodeToGcodeUseCase
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service
from domain.ports.filename_service_port import FilenameServicePort

class SvgToGcodeApp:
    """ Main application class for converting SVG files to G-code. """
    
    def __init__(self):
        file_selector: FileSelectorPort = SvgFileSelectorAdapter()
        self.container = Container(file_selector=file_selector)
        self.filename_service: FilenameServicePort = self.container.filename_gen
        self.config = self.container.config
        self.config_port = self.container.config_port
        self.selector = self.container.selector
        self.logger: LoggerPort = self.container.logger
        self.feed = self.container.feed
        self.cmd_down = self.container.cmd_down
        self.cmd_up = self.container.cmd_up
        self.step_mm = self.container.step_mm
        self.dwell_ms = self.container.dwell_ms
        self.max_height_mm = self.container.max_height_mm
        self.max_width_mm = self.container.max_width_mm
        self.event_bus = self.container.event_bus
        # Suscribimos un handler de ejemplo al evento 'gcode_generated'
        self.event_bus.subscribe('gcode_generated', self._on_gcode_generated)
        # Suscribimos handler para evento de reescalado
        self.event_bus.subscribe('gcode_rescaled', self._on_gcode_rescaled)

    def _on_gcode_generated(self, payload):
        self.logger.info(f"[EVENTO] G-code generado para: {payload['svg_file']} → {payload['gcode_file']}")

    def _on_gcode_rescaled(self, payload):
        self.logger.info(f"[EVENTO] G-code reescalado: {payload['input_file']} → {payload['output_file']} (escala: {payload['scale_factor']:.3f})")

    def _write_gcode_file(self, gcode_file: Path, gcode_lines):
        with gcode_file.open("w", encoding="utf-8") as f:
            f.write("\n".join(gcode_lines))
            
    def _get_context_info(self):
        """Obtener información de contexto para el manejo de excepciones"""
        return {
            "app_version": "1.3.0",
            "config_loaded": bool(self.config),
            "max_dimensions": f"{self.max_width_mm}x{self.max_height_mm}mm"
        }
    
    def _execute_workflow(self):
        """Lógica principal del proceso de conversión"""
        svg_file = self.selector.select_svg_file()
        if not svg_file:
            self.logger.error("No se seleccionó un archivo SVG válido. Operación cancelada.")
            print("[ERROR] No se seleccionó un archivo SVG válido. El proceso ha sido cancelado.")
            return False
            
        svg_file = Path(svg_file)  # Asegura que sea un Path
        self.logger.debug("Selected SVG file: %s", svg_file)
        gcode_file = self.filename_service.next_filename(svg_file)
        self.logger.debug("Output G-code file: %s", gcode_file)

        # Calcular bbox y centro usando GeometryService
        svg_loader_factory = self.container.get_svg_loader
        paths = svg_loader_factory(svg_file).get_paths()
        try:
            bbox = DomainFactory.create_geometry_service()._calculate_bbox(paths)
        except (AttributeError, ValueError):
            bbox = (0, 0, 0, 0)
        _xmin, _xmax, _ymin, _ymax = bbox
        _cx, cy = DomainFactory.create_geometry_service()._center(bbox)
        transform_strategies = []
        # Aplicar transformación vertical solo si está habilitada en la configuración
        if self.config.get_mirror_vertical():
            transform_strategies.append(MirrorVerticalStrategy(cy))

        # Instanciar servicios/casos de uso usando factories
        path_processor = PathProcessingService(
            min_length=1e-3,
            remove_svg_border=self.config.get_remove_svg_border(),
            border_tolerance=self.config.get_border_detection_tolerance()
        )
        generator = self.container.get_gcode_generator(transform_strategies=transform_strategies)
        gcode_service = GCodeGenerationService(generator)
        # Usar la nueva factory para compresión
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
        # Ejecutar caso de uso
        result = svg_to_gcode_use_case.execute(svg_file, transform_strategies=transform_strategies)
        self._write_gcode_file(gcode_file, result['compressed_gcode'])
        self.logger.info("Archivo G-code escrito: %s", gcode_file)
        # Publicar evento tras generar el archivo
        self.event_bus.publish('gcode_generated', {'svg_file': svg_file, 'gcode_file': gcode_file})
        return True

    def select_operation_mode(self):
        print("\n=== Seleccione modo de operación ===")
        print("  [1] SVG a GCODE (conversión estándar)")
        print("  [2] GCODE a GCODE (optimización de archivos existentes)")
        while True:
            try:
                choice = int(input("Seleccione una opción [1-2]: "))
                if choice in [1, 2]:
                    return choice
                print("Opción inválida. Intente nuevamente.")
            except ValueError:
                print("Por favor, ingrese un número válido.")

    def _execute_gcode_to_gcode_workflow(self):
        gcode_selector = GcodeFileSelectorAdapter(self.config)
        gcode_file = gcode_selector.select_gcode_file()
        if not gcode_file:
            self.logger.error("No se seleccionó un archivo GCODE válido. Operación cancelada.")
            print("[ERROR] No se seleccionó un archivo GCODE válido. El proceso ha sido cancelado.")
            return False
        from pathlib import Path
        gcode_file = Path(gcode_file)
        self.logger.debug(f"Archivo GCODE seleccionado: {gcode_file}")

        # Menú de operaciones GCODE→GCODE
        print("\n=== Seleccione la operación a realizar ===")
        print("  [1] Optimizar movimientos (G1 → G0)")
        print("  [2] Reescalar dimensiones")
        print("  [0] Cancelar")
        operation_choice = -1
        while operation_choice not in [0, 1, 2]:
            try:
                operation_choice = int(input("\nSeleccione una opción [0-2]: "))
            except ValueError:
                print("Por favor, ingrese un número válido.")
        if operation_choice == 0:
            print("Operación cancelada por el usuario.")
            return False
        if operation_choice == 1:
            refactor_use_case = GcodeToGcodeUseCase(
                filename_service=self.filename_service,
                logger=self.logger
            )
            result = refactor_use_case.execute(gcode_file)
            self.event_bus.publish('gcode_refactored', {
                'input_file': gcode_file,
                'output_file': result['output_file'],
                'changes': result['changes_made']
            })
            print(f"\n[ÉXITO] Archivo refactorizado guardado en: {result['output_file']}")
            print(f"Se optimizaron {result['changes_made']} movimientos de G1 a G0")
        elif operation_choice == 2:
            from application.use_cases.gcode_rescale_use_case import GcodeRescaleUseCase
            # Obtener altura objetivo (usar configuración o solicitar al usuario)
            target_height = None
            use_config = input("\n¿Usar altura máxima de configuración (250mm)? [S/n]: ").strip().lower()
            if use_config != 'n':
                target_height = self.config.max_height_mm
                print(f"Usando altura máxima: {target_height}mm")
            else:
                while True:
                    try:
                        target_height = float(input("Ingrese altura deseada en mm: "))
                        if target_height <= 0:
                            print("La altura debe ser mayor que cero.")
                        else:
                            break
                    except ValueError:
                        print("Por favor, ingrese un número válido.")
            rescale_use_case = GcodeRescaleUseCase(
                filename_service=self.filename_service,
                logger=self.logger,
                config_provider=self.config
            )
            result = rescale_use_case.execute(gcode_file, target_height)
            self.event_bus.publish('gcode_rescaled', {
                'input_file': gcode_file,
                'output_file': result['output_file'],
                'scale_factor': result['scale_factor'],
                'original_dimensions': result['original_dimensions'],
                'new_dimensions': result['new_dimensions']
            })
            original_dim = result['original_dimensions']
            new_dim = result['new_dimensions']
            print(f"\n[ÉXITO] Archivo reescalado guardado en: {result['output_file']}")
            print(f"Dimensiones originales: {original_dim['width']:.1f}x{original_dim['height']:.1f}mm")
            print(f"Dimensiones nuevas: {new_dim['width']:.1f}x{new_dim['height']:.1f}mm")
            print(f"Factor de escala: {result['scale_factor']:.3f}")
            print(f"Se reescalaron {result['commands_rescaled']['g0g1']} movimientos lineales y {result['commands_rescaled']['g2g3']} arcos")
        return True

    def run(self):
        " Main method to run the SVG to G-code conversion process. "
        error_handler = self.container.error_handler
        operation_mode = self.select_operation_mode()
        if operation_mode == 1:
            result = error_handler.wrap_execution(
                self._execute_workflow,
                self._get_context_info()
            )
        else:
            result = error_handler.wrap_execution(
                self._execute_gcode_to_gcode_workflow,
                self._get_context_info()
            )
        if not result.get('success', False):
            error_info = result.get('message', 'Error desconocido')
            error_type = result.get('error', 'Error')
            print(f"[{error_type.upper()}] {error_info}")

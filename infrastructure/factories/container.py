"""
Path: infrastructure/factories/container.py
Contenedor simple de dependencias para Clean Architecture.
Refactorizado: delega la creación de dependencias a factories por capa.
"""
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.infra_factory import InfraFactory
from infrastructure.events.simple_event_bus import SimpleEventBus
from infrastructure.error_handling.error_handler import ErrorHandler
from infrastructure.factories.gcode_compression_factory import create_gcode_compression_service

from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort
from domain.ports.file_selector_port import FileSelectorPort
from domain.ports.event_bus_port import EventBusPort
from domain.ports.error_handler_port import ErrorHandlerPort
from domain.ports.filename_service_port import FilenameServicePort

from adapters.output.filename_service_adapter import FilenameServiceAdapter

from application.use_cases.path_processing.path_processing_service import PathProcessingService
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from application.use_cases.gcode_compression.compress_gcode_use_case import CompressGcodeUseCase
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase

class Container:
    " Contenedor simple de dependencias para Clean Architecture. "
    def __init__(self, file_selector: FileSelectorPort = None, event_bus: EventBusPort = None, logger: LoggerPort = None, config_path=None):
        self.config = InfraFactory.create_config(config_path) if config_path else InfraFactory.create_config()
        self.config_port: ConfigPort = AdapterFactory.create_config_adapter(self.config)
        self._logger = logger
        self._selector = file_selector  # Inyectado desde el exterior
        self._event_bus = event_bus or SimpleEventBus()
        self._filename_gen = None
        self._error_handler = None
        self._domain_factory = None
        self._path_processing_service = None
        self._gcode_generation_service = None
        self._gcode_compression_service = None
        self._adapter_factory = None
        self._compress_gcode_use_case = None
        self._svg_to_gcode_use_case = None
        self.feed = self.config.feed
        self.cmd_down = self.config.cmd_down
        self.cmd_up = self.config.cmd_up
        self.step_mm = self.config.step_mm
        self.dwell_ms = self.config.dwell_ms
        self.max_height_mm = self.config.plotter_max_area_mm[1]
        self.max_width_mm = self.config.plotter_max_area_mm[0]

    @property
    def logger(self) -> LoggerPort:
        " Devuelve el logger configurado o crea uno por defecto. "
        if self._logger is None:
            self._logger = AdapterFactory.create_logger_adapter()
        return self._logger

    @property
    def selector(self) -> FileSelectorPort:
        " Devuelve el selector de archivos inyectado o lanza un error si no está configurado. "
        if self._selector is None:
            raise ValueError("FileSelectorPort no ha sido inyectado en el contenedor.")
        return self._selector

    @property
    def filename_gen(self) -> FilenameServicePort:
        " Devuelve el servicio de generación de nombres de archivo. "
        if self._filename_gen is None:
            # Suponemos que config.get_gcode_output_dir() devuelve un Path
            output_dir = self.config.get_gcode_output_dir()
            self._filename_gen = FilenameServiceAdapter(output_dir)
        return self._filename_gen

    @property
    def event_bus(self) -> EventBusPort:
        " Devuelve el bus de eventos configurado. "
        return self._event_bus

    @property
    def error_handler(self) -> ErrorHandlerPort:
        " Devuelve el manejador de errores configurado o crea uno por defecto. "
        if self._error_handler is None:
            self._error_handler = ErrorHandler(self.logger)
        return self._error_handler

    @property
    def domain_factory(self):
        " Devuelve la factory de dominio, creando una si no existe. "
        if self._domain_factory is None:
            self._domain_factory = DomainFactory()
        return self._domain_factory

    @property
    def path_processing_service(self):
        " Devuelve el servicio de procesamiento de rutas, creando uno si no existe. "
        if self._path_processing_service is None:
            # Intenta obtener logger e i18n del contenedor si existen
            logger = getattr(self, 'logger', None)
            i18n = getattr(self, 'i18n', None)
            self._path_processing_service = PathProcessingService(logger=logger, i18n=i18n)
        return self._path_processing_service

    @property
    def gcode_generation_service(self):
        " Devuelve el servicio de generación de G-code, creando uno si no existe. "
        if self._gcode_generation_service is None:
            generator = self.get_gcode_generator()
            self._gcode_generation_service = GCodeGenerationService(generator)
        return self._gcode_generation_service

    @property
    def gcode_compression_service(self):
        " Devuelve el servicio de compresión de G-code, creando uno si no existe. "
        if self._gcode_compression_service is None:
            logger = getattr(self, 'logger', None)
            i18n = getattr(self, 'i18n', None)
            self._gcode_compression_service = create_gcode_compression_service(logger=logger, i18n=i18n)
        return self._gcode_compression_service

    @property
    def adapter_factory(self):
        " Devuelve la factory de adaptadores, creando una si no existe. "
        if self._adapter_factory is None:
            self._adapter_factory = AdapterFactory()
        return self._adapter_factory

    @property
    def compress_gcode_use_case(self):
        " Devuelve el caso de uso de compresión de G-code, creando uno si no existe. "
        if self._compress_gcode_use_case is None:
            # Se asume que la factory requiere el servicio de compresión y el config_port
            compression_service = self.gcode_compression_service
            config_reader = self.adapter_factory.create_config_adapter(self.config)
            self._compress_gcode_use_case = CompressGcodeUseCase(compression_service, config_reader)
        return self._compress_gcode_use_case

    @property
    def svg_to_gcode_use_case(self):
        " Devuelve el caso de uso de conversión SVG a G-code, creando uno si no existe. "
        if self._svg_to_gcode_use_case is None:
            svg_loader_factory = self.get_svg_loader
            path_processor = self.path_processing_service
            gcode_service = self.gcode_generation_service
            gcode_compression_use_case = self.compress_gcode_use_case
            logger = self.logger
            filename_service = self.filename_gen
            self._svg_to_gcode_use_case = SvgToGcodeUseCase(
                svg_loader_factory=svg_loader_factory,
                path_processing_service=path_processor,
                gcode_generation_service=gcode_service,
                gcode_compression_use_case=gcode_compression_use_case,
                logger=logger,
                filename_service=filename_service
            )
        return self._svg_to_gcode_use_case

    def get_gcode_generator(self, transform_strategies=None, i18n=None):
        " Devuelve un generador de G-code configurado. "
        path_sampler = AdapterFactory.create_path_sampler(self.step_mm, logger=self.logger)
        return AdapterFactory.create_gcode_generator(
            path_sampler=path_sampler,
            feed=self.feed,
            cmd_down=self.cmd_down,
            cmd_up=self.cmd_up,
            step_mm=self.step_mm,
            dwell_ms=self.dwell_ms,
            max_height_mm=self.config.plotter_max_area_mm[1],
            max_width_mm=self.max_width_mm,
            config=self.config_port,
            logger=self.logger,
            transform_strategies=transform_strategies or [],
            i18n=i18n
        )

    def get_svg_loader(self, svg_file):
        """Devuelve una instancia de SvgLoaderPort para el archivo dado."""
        return AdapterFactory.create_svg_loader(svg_file)

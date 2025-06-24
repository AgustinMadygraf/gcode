"""
Contenedor simple de dependencias para Clean Architecture.
Refactorizado: delega la creación de dependencias a factories por capa.
"""
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.infra_factory import InfraFactory
from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort
from domain.ports.file_selector_port import FileSelectorPort
from domain.ports.event_bus_port import EventBusPort
from domain.ports.error_handler_port import ErrorHandlerPort
from infrastructure.events.simple_event_bus import SimpleEventBus
from infrastructure.error_handling.error_handler import ErrorHandler

class Container:
    def __init__(self, file_selector: FileSelectorPort = None, event_bus: EventBusPort = None):
        self.config = InfraFactory.create_config()
        self.config_port: ConfigPort = AdapterFactory.create_config_adapter(self.config)
        self._logger = None
        self._selector = file_selector  # Inyectado desde el exterior
        self._event_bus = event_bus or SimpleEventBus()
        self._filename_gen = None
        self._error_handler = None
        self.feed = self.config.feed
        self.cmd_down = self.config.cmd_down
        self.cmd_up = self.config.cmd_up
        self.step_mm = self.config.step_mm
        self.dwell_ms = self.config.dwell_ms
        self.max_height_mm = self.config.max_height_mm
        self.max_width_mm = getattr(self.config, 'max_width_mm', 180.0)

    @property
    def logger(self) -> LoggerPort:
        if self._logger is None:
            self._logger = AdapterFactory.create_logger_adapter()
        return self._logger

    @property
    def selector(self) -> FileSelectorPort:
        if self._selector is None:
            raise ValueError("FileSelectorPort no ha sido inyectado en el contenedor.")
        return self._selector

    @property
    def filename_gen(self):
        if self._filename_gen is None:
            self._filename_gen = DomainFactory.create_filename_service(self.config)
        return self._filename_gen

    @property
    def event_bus(self) -> EventBusPort:
        return self._event_bus

    @property
    def error_handler(self) -> ErrorHandlerPort:
        if self._error_handler is None:
            self._error_handler = ErrorHandler(self.logger)
        return self._error_handler

    def get_gcode_generator(self, transform_strategies=None):
        path_sampler = AdapterFactory.create_path_sampler(self.step_mm, logger=self.logger)
        return AdapterFactory.create_gcode_generator(
            path_sampler=path_sampler,
            feed=self.feed,
            cmd_down=self.cmd_down,
            cmd_up=self.cmd_up,
            step_mm=self.step_mm,
            dwell_ms=self.dwell_ms,
            max_height_mm=self.max_height_mm,
            max_width_mm=self.max_width_mm,
            config=self.config_port,
            logger=self.logger,
            transform_strategies=transform_strategies or []
        )

    def get_svg_loader(self, svg_file):
        """Devuelve una instancia de SvgLoaderPort para el archivo dado."""
        return AdapterFactory.create_svg_loader(svg_file)

    # Agregar más factories según sea necesario

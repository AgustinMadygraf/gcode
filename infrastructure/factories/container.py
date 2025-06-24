"""
Contenedor simple de dependencias para Clean Architecture.
Refactorizado: delega la creación de dependencias a factories por capa.
"""
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.factories.domain_factory import DomainFactory
from infrastructure.factories.infra_factory import InfraFactory
from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort
from cli.svg_file_selector import SvgFileSelector

class Container:
    def __init__(self):
        self.config = InfraFactory.create_config()
        self.config_port: ConfigPort = AdapterFactory.create_config_adapter(self.config)
        self._logger = None
        self._selector = None
        self._filename_gen = None
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
    def selector(self):
        if self._selector is None:
            self._selector = SvgFileSelector(self.config.svg_input_dir)
        return self._selector

    @property
    def filename_gen(self):
        if self._filename_gen is None:
            self._filename_gen = DomainFactory.create_filename_service(self.config)
        return self._filename_gen

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

"""
Contenedor simple de dependencias para Clean Architecture.
Permite centralizar wiring y facilitar testing/mocks.
"""
from pathlib import Path
from infrastructure.config.config import Config
from adapters.input.config_adapter import ConfigAdapter
from domain.ports.config_port import ConfigPort
from cli.svg_file_selector import SvgFileSelector
from infrastructure.logger import logger
from adapters.input.svg_loader_adapter import SvgLoaderAdapter
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from adapters.input.path_sampler import PathSampler
from domain.services.geometry import GeometryService
from application.use_cases.file_output.filename_service import FilenameService
from adapters.output.logger_adapter import LoggerAdapter
from domain.ports.logger_port import LoggerPort

class Container:
    def __init__(self):
        self.config = Config(Path("infrastructure/config/config.json"))
        self.config_port: ConfigPort = ConfigAdapter(self.config)
        self.logger: LoggerPort = LoggerAdapter()
        self.selector = SvgFileSelector(self.config.svg_input_dir)
        self.filename_gen = FilenameService(self.config)
        self.feed = self.config.feed
        self.cmd_down = self.config.cmd_down
        self.cmd_up = self.config.cmd_up
        self.step_mm = self.config.step_mm
        self.dwell_ms = self.config.dwell_ms
        self.max_height_mm = self.config.max_height_mm
        self.max_width_mm = getattr(self.config, 'max_width_mm', 180.0)

    def get_gcode_generator(self, transform_strategies=None):
        path_sampler = PathSampler(self.step_mm, logger=self.logger)
        return GCodeGeneratorAdapter(
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

    # Agregar más factories según sea necesario

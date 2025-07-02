"""
Path: infrastructure/factories/adapter_factory/__init__.py
Factory para adaptadores (input/output) de la capa de Interface Adapters.
"""
from adapters.input.config_adapter import ConfigAdapter
from adapters.input.svg_loader_adapter import SvgLoaderAdapter
from adapters.input.path_sampler import PathSampler
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from adapters.output.logger_adapter import LoggerAdapter

class AdapterFactory:
    @staticmethod
    def create_config_adapter(config):
        return ConfigAdapter(config)

    @staticmethod
    def create_svg_loader(svg_file):
        return SvgLoaderAdapter(svg_file)

    @staticmethod
    def create_path_sampler(step_mm, logger):
        return PathSampler(step_mm, logger=logger)

    @staticmethod
    def create_gcode_generator(**kwargs):
        return GCodeGeneratorAdapter(**kwargs)

    @staticmethod
    def create_logger_adapter():
        return LoggerAdapter()

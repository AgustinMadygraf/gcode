"""
Test de flag de debug en GCodeGeneratorAdapter: verifica que el logger.debug solo se llama si el flag está activo.
"""
import pytest
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.config_port import ConfigPort

class DummyPathSampler(PathSamplerPort):
    def sample(self, *a, **kw):
        return []

class DummyLogger:
    def __init__(self):
        self.debug_called = False
        self.last_msg = None
    def debug(self, msg, *a, **k):
        self.debug_called = True
        self.last_msg = msg
    def info(self, *a, **k): pass
    def error(self, *a, **k): pass
    def warning(self, *a, **k): pass

class DummyConfigDebugOn(ConfigPort):
    def get_debug_flag(self, name):
        return True
    def get_compression_config(self):
        return None
    def get(self, *a, **k):
        return None

class DummyConfigDebugOff(ConfigPort):
    def get_debug_flag(self, name):
        return False
    def get_compression_config(self):
        return None
    def get(self, *a, **k):
        return None

def test_debug_flag_triggers_logger():
    logger = DummyLogger()
    adapter = GCodeGeneratorAdapter(
        path_sampler=DummyPathSampler(),
        feed=1000.0,
        cmd_down="M3",
        cmd_up="M5",
        step_mm=1.0,
        dwell_ms=0,
        max_height_mm=100.0,
        config=DummyConfigDebugOn(),
        logger=logger
    )
    adapter._debug("Mensaje de debug")
    assert logger.debug_called, "El logger.debug no fue llamado cuando el flag está activo"
    assert logger.last_msg == "Mensaje de debug"

def test_debug_flag_blocks_logger():
    logger = DummyLogger()
    adapter = GCodeGeneratorAdapter(
        path_sampler=DummyPathSampler(),
        feed=1000.0,
        cmd_down="M3",
        cmd_up="M5",
        step_mm=1.0,
        dwell_ms=0,
        max_height_mm=100.0,
        config=DummyConfigDebugOff(),
        logger=logger
    )
    adapter._debug("Mensaje de debug")
    assert not logger.debug_called, "El logger.debug fue llamado cuando el flag está desactivado"
